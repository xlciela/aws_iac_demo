#!/bin/bash

# 创建apiuser用户配置脚本
# 在EC2实例上以root权限运行此脚本

echo "开始配置apiuser..."

# 1. 创建apiuser用户（如果不存在）
if ! id "apiuser" &>/dev/null; then
    echo "创建apiuser用户..."
    useradd -m -s /bin/bash apiuser
else
    echo "apiuser用户已存在"
fi

# 2. 设置apiuser密码
echo "设置apiuser密码..."
echo "apiuser:291Lix8K" | chpasswd

# 3. 创建.ssh目录并设置权限
echo "配置SSH目录和密钥..."
mkdir -p /home/apiuser/.ssh
chmod 700 /home/apiuser/.ssh

# 4. 复制authorized_keys
if [ -f /home/ec2-user/.ssh/authorized_keys ]; then
    cp /home/ec2-user/.ssh/authorized_keys /home/apiuser/.ssh/
    echo "已复制authorized_keys文件"
else
    echo "警告: /home/ec2-user/.ssh/authorized_keys 文件不存在"
fi

# 5. 设置正确的文件权限
chmod 600 /home/apiuser/.ssh/authorized_keys 2>/dev/null
chown -R apiuser:apiuser /home/apiuser/.ssh

# 6. 配置SSHD
echo "配置SSHD..."
# 备份原配置
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 确保密码认证启用
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# 确保公钥认证启用
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# 确保允许用户登录
if ! grep -q "AllowUsers" /etc/ssh/sshd_config; then
    echo "AllowUsers ec2-user apiuser" >> /etc/ssh/sshd_config
else
    # 如果已存在AllowUsers，确保包含apiuser
    if ! grep "AllowUsers" /etc/ssh/sshd_config | grep -q "apiuser"; then
        sed -i 's/AllowUsers.*/& apiuser/' /etc/ssh/sshd_config
    fi
fi

# 添加Match规则限制apiuser访问
if ! grep -q "Match User apiuser" /etc/ssh/sshd_config; then
    echo "" >> /etc/ssh/sshd_config
    echo "Match User apiuser" >> /etc/ssh/sshd_config
fi

# 7. 重启SSH服务
echo "重启SSH服务..."
systemctl restart sshd

# 8. 验证配置
echo "验证配置..."
echo "用户信息:"
id apiuser

echo "SSH目录权限:"
ls -la /home/apiuser/.ssh/

echo "SSHD配置检查:"
grep -E "(PasswordAuthentication|PubkeyAuthentication|AllowUsers)" /etc/ssh/sshd_config

echo "配置完成！"
echo "现在可以尝试以下连接方式："
echo "1. 使用密码: ssh apiuser@YOUR_IP"
echo "2. 使用密钥: ssh -i your_key.pem apiuser@YOUR_IP"