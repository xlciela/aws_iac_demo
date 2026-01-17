rpm -qa | grep -i httpd
yum install httpd -y

systemctl start httpd
systemctl enable httpd # to start on boot

# firewall-cmd --permanent --add-service=https
# add http service to firewall
# firewall-cmd --permanent --add-service=httpd
# reload firewall
# firewall-cmd --reload
# systemctl restart httpd

# congigure SELinux to allow httpd to make network connections
# setsebool -P httpd_can_network_connect on

cd /home/apigwuser/public_html
vim index.html
# echo "<h1>Welcome to Apache HTTP Server on EC2</h1>" > index.html
chomod -R 755 /home/apigwuser/

# congiguration
# vim /etc/httpd/conf/httpd.conf
vim /etc/httpd/conf.d/userdir.conf
# -> UserDir enabled
# -> UserDir public_html
# Fire