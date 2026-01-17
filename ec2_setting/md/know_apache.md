# What is Apache
It is designed to serve web content over the internet. 
### 实际上是一个监听电脑端口的进程
" 每当输入目标域名/地址, apache就会查找对应的目标目录和文件, 返回网页
# what can Apache do
## deploy web app
Apache can host static websites, dynamic web applications, and APIs. It supports various programming languages through modules, such as PHP, Python, and Perl.
## handle multiple requests
Apache can handle multiple client requests simultaneously using a multi-threaded or multi-process architecture, ensuring efficient resource utilization and responsiveness.
## support modules
Apache has a modular architecture that allows users to extend its functionality by adding or removing modules. This enables features like SSL/TLS support, URL rewriting, authentication, and caching.
* mod_rewrite
    用于伪静态, 改善SEO和URL管理
* mod_ssl
    开启HTTPS, 加密网站数据传输
* mod_php
    支持Apache运行PHP页面, 扩展功能
## combine with Ngnix, Tomcat to build complex 反向代理, 负载均衡
## automate deployment process
