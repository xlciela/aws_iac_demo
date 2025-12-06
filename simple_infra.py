# vpc+ subnet
# s3 bucket
# EC2@subnet
from troposphere import Template, Ref
import troposphere.ec2 as ec2
import troposphere.s3 as s3

t = Template()
t.set_description("Simple infrastructure with VPC, Subnet, S3 Bucket, and EC2 Instance")

# 1. Create VPC
my_vpc = t.add_resource(ec2.VPC(
    "MyVPC",
    CidrBlock="10.0.0.0/16",
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    Tags=[ec2.Tag("Name", "MyVPC")]
    ))

# 2. Create Subnet in the VPC
my_subnet = t.add_resource(ec2.Subnet(
    "MySubnet",
    CidrBlock="10.0.0.0/24",
    VpcId=Ref(my_vpc),
    MapPublicIpOnLaunch=True,
    Tags=[ec2.Tag("Name", "MySubnet")]
    ))
# 3. Create S3 Bucket
my_bucket = t.add_resource(s3.Bucket(
    "MyS3Bucket",
    BucketName="my-unique-bucket-name-1234567890",
    AccessControl=s3.Private
    ))
# 4. Create EC2 Instance in the Subnet
my_instance = t.add_resource(ec2.Instance(
    "MyEC2Instance",
    InstanceType="t2.micro",
    # ImageId="ami-0c55b159cbfafe1f0",
    SubnetId=Ref(my_subnet),
    Tags=[ec2.Tag("Name", "MyEC2Instance")]
    ))

# output the template to yaml
with open("simple_infra.yaml", "w") as f:
    f.write(t.to_yaml())

print("generated CloudFormation CFT file: simple_infra.yaml") 
