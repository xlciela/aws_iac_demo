#!/usr/bin/env python3
"""
VPC Peering 连接验证脚本
用于检查VPC Peering连接状态和路由配置
"""

import boto3
import json
from botocore.exceptions import ClientError

def check_vpc_peering_status(stack_name):
    """检查VPC Peering连接状态"""
    try:
        # 初始化AWS客户端
        cf_client = boto3.client('cloudformation')
        ec2_client = boto3.client('ec2')
        
        # 获取栈输出
        response = cf_client.describe_stacks(StackName=stack_name)
        stack_outputs = response['Stacks'][0]['Outputs']
        
        # 提取关键信息
        peering_id = None
        vpc_a_id = None
        vpc_b_id = None
        
        for output in stack_outputs:
            if output['OutputKey'] == 'VpcPeeringConnectionId':
                peering_id = output['OutputValue']
            elif output['OutputKey'] == 'VpcAId':
                vpc_a_id = output['OutputValue']
            elif output['OutputKey'] == 'VpcBId':
                vpc_b_id = output['OutputValue']
        
        print(f"🔍 检查VPC Peering连接状态...")
        print(f"Peering Connection ID: {peering_id}")
        print(f"VPC A ID: {vpc_a_id}")
        print(f"VPC B ID: {vpc_b_id}")
        print("-" * 50)
        
        # 检查Peering连接状态
        peering_response = ec2_client.describe_vpc_peering_connections(
            VpcPeeringConnectionIds=[peering_id]
        )
        
        peering_conn = peering_response['VpcPeeringConnections'][0]
        status = peering_conn['Status']['Code']
        
        print(f"📊 Peering连接状态: {status}")
        
        if status == 'active':
            print("✅ VPC Peering连接已激活")
        else:
            print(f"❌ VPC Peering连接状态异常: {status}")
            return False
        
        # 检查路由表配置
        print("\n🛣️  检查路由表配置...")
        
        # 获取VPC A的路由表
        vpc_a_routes = ec2_client.describe_route_tables(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_a_id]}]
        )
        
        # 获取VPC B的路由表
        vpc_b_routes = ec2_client.describe_route_tables(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_b_id]}]
        )
        
        # 检查VPC A到VPC B的路由
        vpc_a_has_route = False
        for rt in vpc_a_routes['RouteTables']:
            for route in rt['Routes']:
                if (route.get('DestinationCidrBlock') == '10.1.0.0/16' and 
                    route.get('VpcPeeringConnectionId') == peering_id):
                    vpc_a_has_route = True
                    print("✅ VPC A -> VPC B 路由配置正确")
                    break
        
        if not vpc_a_has_route:
            print("❌ VPC A -> VPC B 路由配置缺失")
        
        # 检查VPC B到VPC A的路由
        vpc_b_has_route = False
        for rt in vpc_b_routes['RouteTables']:
            for route in rt['Routes']:
                if (route.get('DestinationCidrBlock') == '10.0.0.0/16' and 
                    route.get('VpcPeeringConnectionId') == peering_id):
                    vpc_b_has_route = True
                    print("✅ VPC B -> VPC A 路由配置正确")
                    break
        
        if not vpc_b_has_route:
            print("❌ VPC B -> VPC A 路由配置缺失")
        
        # 获取测试实例信息
        print("\n🖥️  获取测试实例信息...")
        
        # VPC A实例
        vpc_a_instances = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['VPC-A-Test-Instance']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        # VPC B实例
        vpc_b_instances = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['VPC-B-Test-Instance']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        if vpc_a_instances['Reservations']:
            vpc_a_ip = vpc_a_instances['Reservations'][0]['Instances'][0]['PrivateIpAddress']
            print(f"VPC A 测试实例私有IP: {vpc_a_ip}")
        else:
            print("❌ VPC A 测试实例未找到或未运行")
        
        if vpc_b_instances['Reservations']:
            vpc_b_ip = vpc_b_instances['Reservations'][0]['Instances'][0]['PrivateIpAddress']
            print(f"VPC B 测试实例私有IP: {vpc_b_ip}")
        else:
            print("❌ VPC B 测试实例未找到或未运行")
        
        # 总结
        print("\n📋 验证总结:")
        if status == 'active' and vpc_a_has_route and vpc_b_has_route:
            print("✅ VPC Peering配置完成，可以进行连接测试")
            print("\n🔧 测试连接命令:")
            if vpc_a_instances['Reservations'] and vpc_b_instances['Reservations']:
                print(f"从VPC A实例ping VPC B: ping {vpc_b_ip}")
                print(f"从VPC B实例ping VPC A: ping {vpc_a_ip}")
        else:
            print("❌ VPC Peering配置存在问题，请检查上述错误")
        
        return True
        
    except ClientError as e:
        print(f"❌ AWS API错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 脚本执行错误: {e}")
        return False

if __name__ == "__main__":
    stack_name = "vpc-peering-demo"
    print("🚀 开始验证VPC Peering配置...")
    print("=" * 60)
    
    success = check_vpc_peering_status(stack_name)
    
    if success:
        print("\n✅ 验证完成")
    else:
        print("\n❌ 验证失败")