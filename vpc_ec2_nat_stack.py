'''
Amazon VPC
Subnet*2 (public / private)
Internet Gateway + RouteTable@public -> IGW 
NAT Gateway + RouteTable@private -> NAT
EC2 instance*2(1@public subnet，1@private subnet)
public.SecurityGroup (approve SSH / HTTP) + private.SecurityGroup (approve NAT)
'''
from bs4 import Tag
from sympy import Ci, public
from troposphere import Template, Ref, Join, GetAtt, Sub
import troposphere.ec2 as ec2
# import troposphere.iam as iam
# import troposphere.elasticloadbalancing as elb
# import troposphere.s3 as s3
from troposphere import Output

t = Template()
t.set_description("VPC with Public and Private Subnets, NAT Gateway, and EC2 Instances")

# 1. Create VPC
vpc = t.add_resource(ec2.VPC(
    "MyVPC",
    CidrBlock="10.0.0.0/16",
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    Tags=[ec2.Tag("Name", "MyVPC")]
))

# 2. Create Internet Gateway & Attach to VPC
igw = t.add_resource(ec2.InternetGateway(
    "MyInternetGateway",
    Tags=[ec2.Tag("Name", "my-igw")]
))
t.add_resource(ec2.VPCGatewayAttachment(
    "AttachIGW",
    VpcId=Ref(vpc),
    InternetGatewayId=Ref(igw)
))

# 3. Subnets
public_subnet = t.add_resource(ec2.Subnet(
    "PublicSubnet",
    CidrBlock="10.0.0.0/24", # available IP_count = 256-2=254
    MapPublicIpOnLaunch=True, # auto assign public IP for instances created here
    VpcId=Ref(vpc), # define in which VPC the subnet is created
    Tags=[ec2.Tag("Name", "public-subnet")]
))
private_subnet = t.add_resource(ec2.Subnet(
    "PrivateSubnet",
    CidrBlock="10.0.1.0/24", # available IP_count = 254
    MapPublicIpOnLaunch=False,
    Tags=[ec2.Tag('Name', 'private-subnet')] 
))

# 4. RouteTable for public subnet, route to IGW
# create RT
public_rt = t.add_resource(ec2.RouteTable(
    'PublicRouteTable',
    VpcId=Ref(vpc),
    Tags=[ec2.Tag('Name', 'public-rt')]
))
# add rules@RT
# TODO: add local rule firstly

t.add_resource(ec2.Route(
    "PublicDefaultRoute",
    RouteTableId=Ref(public_rt),# define target RT@public_rt 
    DestinationCidrBlock="0.0.0.0/0", # range
    GatewayId=Ref(igw) # next
))
# define to which the RouteTable applies
t.add_resource(ec2.SubnetRouteTableAssociation(
    "PublicSubnetRTAssoc",
    SubnetId=Ref(public_subnet),
    RouteTableId=(public_rt)
))

# 5. NAT(in public_subnet)
eip = t.add_resource(ec2.EIP(
    "NATIP", # logical name only applied @template/stack level, not the actual AWS Resource Id
    Domain="VPC" # TODO: VPC level
))
'''
AllocationId: 
The allocation ID of the Elastic IP address that's associated with the NAT gateway. 
This property is required for a public NAT gateway 
    and cannot be specified with a private NAT gateway.
AllocationId vs InstanceId(@ec2 instance)   
AllocationId — 是 EIP 分配完成后 AWS 返回给你的一个内部标识符 (allocation ID)。
这个 ID 用于 “将 EIP 与其他资源绑定 / 或给 NAT Gateway 这样需要公网 IP 的 AWS 资源”。
也就是说，不是绑定 EC2，而是绑定 NAT Gateway、网络接口 (ENI) 等资源

The Fn::GetAtt intrinsic function (logicalNameOfResource, attributeName)-> attributeValue
    returns the value of an attribute from a resource in the template.
'''
nat_gw = t.add_resource(ec2.NatGateway(
    "NATGateway",
    SubnetId=Ref(public_subnet),
    AllocationId=GetAtt(eip, "AllocationId"), # get the attr of the eip created before
    Tags=[ec2.Tag("Name", "my-nat-gateway")]
))

# 5. RT for private subnet( 0.0.0.0/0 via NAT) 
# RouteTable itself
private_rt = t.add_resource(ec2.RouteTable(
    "PrivateRouteTable",
    VpcId=Ref(vpc),
    Tags=[ec2.Tag("Name", "private-rt")]
))
# RouteTable's rules
t.add_resource(ec2.Route(
    "PrivateDefaultRoute",
    RouteTableId=Ref(private_rt), # RT
    DestinationCidrBlock="0.0.0.0/0", # range
    NatGatewayId=Ref(nat_gw) # next
))
# associate the RT with the private subnet
t.add_resource(ec2.SubnetRouteTableAssociation(
    "PrivateSubnetRTAssoc",
    SubnetId=Ref(private_subnet),
    RouteTableId=Ref(private_rt)
))

# 7. SGs
# public SG ( allow ssh, http from anywhere)
public_sg = t.add_resource(ec2.SecurityGroup(
    "PublicSG",
    GroupDescription="Allow SSH, HTTP from anywhere",
    VpcId=Ref(vpc),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=22, ToPort=22, CidrIp="0.0.0.0/0"),
        ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=80, ToPort=80, CidrIp="0.0.0.0/0")
    ],
    # allow all outbound traffic
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(IpProtocol="-1", FromPort=0, ToPort=65535, CidrIp="0.0.0.0/0")
    ],
    Tags=[ec2.Tag("Name", "public-sg")]
))
# private SG
private_sg = t.add_resource(ec2.SecurityGroup(
    "PrivateSG",
    GroupDescription="Private subnet SG – allow all outbound",
    VpcId=Ref(vpc),
    # allow all outbound, rely on NAT
    SecurityGroupEgress=[
        ec2.SecurityGroupRule(IpProtocol="-1", FromPort=0, ToPort=65535, CidrIp="0.0.0.0/0")
    ],
    Tags=[{"Key": "Name", "Value": "private-sg"}]
))

# 8. ec2 instances
ami_id = "ami-03852a41f1e05c8e4"

public_instance = t.add_resource(ec2.Instance(
    "PublicInstance",
    InstanceType="t2.micro",
    SubnetId=Ref(public_subnet),
    ImageId=ami_id,
    SecurityGroupIds=[Ref(public_sg)],
    Tags=[ec2.Tag("Name", "public-ec2")]
))

private_instance = t.add_resource(ec2.Instance(
    "PrivateInstance",
    InstanceType="t2.micro",
    SubnetId=Ref(private_subnet),
    ImageId=ami_id,
    SecurityGroupIds=[Ref(private_sg)],
    Tags=[{"Key": "Name", "Value": "private-ec2"}]
))

# 9. TODO: (optional) Outputs?
t.add_output(Output(
    "PublicInstanceId",
    Value=Ref(public_instance)
))
t.add_output(Output(
    "PrivateInstanceId",
    Value=Ref(private_instance)
))

with open("vpc_nat_ec2.yaml", "w") as f:
    f.write(t.to_yaml())

print("Generated template vpc_nat_ec2.yaml")