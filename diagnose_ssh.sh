#!/bin/bash

# SSH连接故障排除脚本
# 在EC2实例上运行以诊断SSH连接问题

echo "=== SSH连接故障排除 ==="
echo

# 1. 检查用户是否存在
echo "1. 检查用户状态:"
if id "apiuser" &>/dev/null; then
    echo "✓ apiuser用户存在"
    id apiuser
else
    echo "✗ apiuser用户不存在"
fi
echo

# 2. 检查用户密码状态
echo "2. 检查密码状态:"
passwd_status=$(passwd -S apiuser 2>/dev/null | awk '{print $2}')
if [ "$passwd_status" = "P" ]; then
    echo "✓ apiuser密码已设置"
elif [ "$passwd_status" = "L" ]; then
    echo "✗ apiuser账户被锁定"
elif [ "$passwd_status" = "NP" ]; then
    echo "✗ apiuser没有密码"
else
    echo "? apiuser密码状态未知: $passwd_status"
fi
echo

# 3. 检查SSH目录和文件权限
echo "3. 检查SSH配置:"
if [ -d "/home/apiuser/.ssh" ]; then
    echo "✓ .ssh目录存在"
    ls -la /home/apiuser/.ssh/
    
    # 检查权限
    ssh_dir_perm=$(stat -c "%a" /home/apiuser/.ssh)
    if [ "$ssh_dir_perm" = "700" ]; then
        echo "✓ .ssh目录权限正确 (700)"
    else
        echo "✗ .ssh目录权限错误: $ssh_dir_perm (应该是700)"
    fi
    
    if [ -f "/home/apiuser/.ssh/authorized_keys" ]; then
        echo "✓ authorized_keys文件存在"
        auth_keys_perm=$(stat -c "%a" /home/apiuser/.ssh/authorized_keys)
        if [ "$auth_keys_perm" = "600" ]; then
            echo "✓ authorized_keys权限正确 (600)"
        else
            echo "✗ authorized_keys权限错误: $auth_keys_perm (应该是600)"
        fi
    else
        echo "✗ authorized_keys文件不存在"
    fi
else
    echo "✗ .ssh目录不存在"
fi
echo

# 4. 检查文件所有者
echo "4. 检查文件所有者:"
if [ -d "/home/apiuser/.ssh" ]; then
    owner=$(stat -c "%U:%G" /home/apiuser/.ssh)
    if [ "$owner" = "apiuser:apiuser" ]; then
        echo "✓ .ssh目录所有者正确"
    else
        echo "✗ .ssh目录所有者错误: $owner (应该是apiuser:apiuser)"
    fi
fi
echo

# 5. 检查SSHD配置
echo "5. 检查SSHD配置:"
echo "密码认证:"
grep -E "^PasswordAuthentication" /etc/ssh/sshd_config || echo "未找到PasswordAuthentication配置"

echo "公钥认证:"
grep -E "^PubkeyAuthentication" /etc/ssh/sshd_config || echo "未找到PubkeyAuthentication配置"

echo "允许用户:"
grep -E "^AllowUsers" /etc/ssh/sshd_config || echo "未找到AllowUsers配置"

echo "拒绝用户:"
grep -E "^DenyUsers" /etc/ssh/sshd_config || echo "未找到DenyUsers配置"
echo

# 6. 检查SSH服务状态
echo "6. 检查SSH服务状态:"
systemctl is-active sshd
systemctl is-enabled sshd
echo

# 7. 检查防火墙和安全组
echo "7. 检查网络连接:"
echo "SSH端口监听状态:"
netstat -tlnp | grep :22 || ss -tlnp | grep :22
echo

# 8. 检查日志
echo "8. 最近的SSH认证日志:"
tail -10 /var/log/secure 2>/dev/null || tail -10 /var/log/auth.log 2>/dev/null || echo "无法读取认证日志"
echo

echo "=== 故障排除完成 ==="
echo
echo "建议的修复步骤:"
echo "1. 如果用户不存在，运行: sudo useradd -m -s /bin/bash apiuser"
echo "2. 如果密码未设置，运行: sudo echo 'apiuser:291Lix8K' | chpasswd"
echo "3. 如果权限错误，运行: sudo chmod 700 /home/apiuser/.ssh && sudo chmod 600 /home/apiuser/.ssh/authorized_keys"
echo "4. 如果所有者错误，运行: sudo chown -R apiuser:apiuser /home/apiuser/.ssh"
echo "5. 如果SSHD配置错误，编辑 /etc/ssh/sshd_config 并重启服务"