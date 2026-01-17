#!/bin/bash

echo "=== /home目录下用户密码状态检查 ==="
echo

# 检查/home下的所有用户
for user_dir in /home/*; do
    if [ -d "$user_dir" ]; then
        username=$(basename "$user_dir")
        echo "用户: $username"
        
        # 检查用户是否在系统中存在
        if id "$username" &>/dev/null; then
            # 获取密码状态
            passwd_info=$(sudo passwd -S "$username" 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo "  密码状态: $passwd_info"
                
                # 解析状态
                status=$(echo "$passwd_info" | awk '{print $2}')
                case $status in
                    "P")  echo "  状态说明: 密码已设置" ;;
                    "NP") echo "  状态说明: 无密码" ;;
                    "L")  echo "  状态说明: 账户被锁定" ;;
                    "PS") echo "  状态说明: 密码已设置且账户未锁定" ;;
                    *)    echo "  状态说明: 未知状态 ($status)" ;;
                esac
                
                # 显示shadow文件中的条目（加密密码）
                shadow_entry=$(sudo grep "^$username:" /etc/shadow 2>/dev/null)
                if [ -n "$shadow_entry" ]; then
                    echo "  Shadow条目: $shadow_entry"
                    # 提取密码字段
                    password_field=$(echo "$shadow_entry" | cut -d: -f2)
                    if [ "$password_field" = "!" ] || [ "$password_field" = "*" ]; then
                        echo "  密码字段: 账户被禁用"
                    elif [ -z "$password_field" ]; then
                        echo "  密码字段: 无密码"
                    else
                        echo "  密码字段: 已加密 (${#password_field}字符)"
                    fi
                fi
            else
                echo "  无法获取密码状态"
            fi
        else
            echo "  用户不存在于系统中"
        fi
        echo
    fi
done

echo "注意: 密码以加密形式存储，无法查看明文密码"