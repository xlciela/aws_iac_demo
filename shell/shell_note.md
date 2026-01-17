### 条件语句
```bash
if [condition]; then
    # do sth
fi

if [cond]; then
    # do sth
else
    # do sth
fi
```
例：
```bash
#!/bin/bash
# check whether target folder exist
TARGET_DIR="/home/user/target_folder"
if -d ${TARGET_DIR}; then
    echo "Target folder exists."
else
    echo "Target folder does not exist."
fi
```
### loop
```bash
for var in list; do
    # do sth
done
```
例1：
```bash
#!/bin/bash
# print all files in target folder
TARGET_DIR="/home/user/target_folder"
for file in ${TARGET_DIR}/*; do
    echo ${file}
done
```
例2：
```bash
#!/bin/bash
for i in $(cat /shell/uname.log);
do
    useradd ${i}
    echo "added user: ${i}"
done
# test
id Lain
```
### while loop
```bash
#!/bin/bash
while [condition]; do
    # do sth
done
```
例：
```bash
#!/bin/bash
# print numbers from 1 to 5
count=1
while [ ${count} -le 5 ]; do
    echo ${count}
    ((count++))
done
```  
### case 语句
```bash
#!/bin/bash
case variable in
    pattern1)
        # do sth
        ;;
    pattern21 | pattern22)
        # do sth
        ;;
    *) # default branch
        # do sth
        ;;
esac # end case
```
例：
```bash
#!/bin/bash
# check internet status
ping -c 1 google.com > /dev/null 2>&1
case $? in # $? is the exit status of the last command
    0)
        echo "Internet is connected."
        ;;
    1)
        echo "Internet is not connected."
        ;;
    *)
        echo "Unknown error occurred."
        ;;
esac
```
例2：
```bash
#!/bin/bash
#!/bin/bash
service_status=$(systemctl is-active nginx)

case $service_status in
    active)
        echo "Nginx 正在运行"
        ;;
    inactive)
        echo "Nginx 未运行 X → 启动中..."
        systemctl start nginx
        ;;
    failed)
        echo "Nginx 启动失败 -> 尝试修复..."
        systemctl reset-failed nginx
        ;;
    unknow)
        echo "Ngnix doesn't work"
        ;; 
esac
```