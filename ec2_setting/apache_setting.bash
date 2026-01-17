# confirm whether apache is installed
rpm -qa | grep httpd
# install apache
yum install httpd -y
rpm -qa | grep httpd
# start apache
systemctl start httpd
systemctl enable httpd # enable apache to start on boot
# check status
systemctl status httpd
