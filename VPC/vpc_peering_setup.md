# VPC Peering 配置步骤指南

## 1. 部署CloudFormation模板

```bash
# 部署VPC Peering栈
aws cloudformation create-stack \
  --stack-name vpc-peering-demo \
  --template-body file://vpc_peering_demo.yaml \
  --region ap-northeast-1

# 检查部署状态
aws cloudformation describe-stacks \
  --stack-name vpc-peering-demo \
  --region ap-northeast-1
```

## 2. VPC Peering 连接原理

### 关键概念：
- **VPC Peering**: 两个VPC之间的网络连接，允许私有IP通信
- **路由配置**: 必须在两个VPC的路由表中添加对方的CIDR路由
- **安全组**: 需要配置允许对方VPC的流量

### 网络架构：
```
VPC A (10.0.0.0/16)     <------ VPC Peering ------>     VPC B (10.1.0.0/16)
├── Public Subnet (10.0.1.0/24)                         ├── Public Subnet (10.1.1.0/24)
└── Private Subnet (10.0.2.0/24)                        └── Private Subnet (10.1.2.0/24)
```

## 3. 路由配置详解

### VPC A 路由表配置：
- 目标: 10.1.0.0/16 (VPC B的CIDR)
- 目标: VPC Peering Connection ID

### VPC B 路由表配置：
- 目标: 10.0.0.0/16 (VPC A的CIDR)
- 目标: VPC Peering Connection ID

## 4. 验证连接

### 获取实例信息：
```bash
# 获取VPC A实例的私有IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=VPC-A-Test-Instance" \
  --query 'Reservations[*].Instances[*].PrivateIpAddress' \
  --output text

# 获取VPC B实例的私有IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=VPC-B-Test-Instance" \
  --query 'Reservations[*].Instances[*].PrivateIpAddress' \
  --output text
```

### 连接测试：
```bash
# 从VPC A实例ping VPC B实例
# 需要先通过Session Manager或其他方式连接到实例
ping <VPC-B-实例私有IP>

# 从VPC B实例ping VPC A实例
ping <VPC-A-实例私有IP>
```

## 5. 故障排除

### 常见问题：
1. **Peering连接状态**: 确保状态为"active"
2. **路由表配置**: 检查两边路由表都有对方的CIDR路由
3. **安全组规则**: 确保安全组允许对方VPC的流量
4. **NACL规则**: 检查网络ACL是否阻止流量

### 检查命令：
```bash
# 检查VPC Peering连接状态
aws ec2 describe-vpc-peering-connections \
  --filters "Name=status-code,Values=active"

# 检查路由表
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=<VPC-ID>"

# 检查安全组规则
aws ec2 describe-security-groups \
  --group-ids <SECURITY-GROUP-ID>
```

## 6. 清理资源

```bash
# 删除CloudFormation栈
aws cloudformation delete-stack \
  --stack-name vpc-peering-demo \
  --region ap-northeast-1
```

## 7. 最佳实践

### 安全考虑：
- 只开放必要的端口和协议
- 使用最小权限原则配置安全组
- 定期审查Peering连接的必要性

### 网络设计：
- 避免CIDR重叠
- 合理规划子网大小
- 考虑未来扩展需求

### 成本优化：
- VPC Peering本身不收费
- 跨AZ流量会产生费用
- 监控数据传输量