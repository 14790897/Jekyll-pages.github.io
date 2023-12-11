---
title: 如何使用acme指令安装证书？
date: 2023-05-08
layout: single
categories: lifestyle
---

以下是使用 acme.sh 脚本为 `*.liuweiqing.top` 域名申请和安装 Let's Encrypt 泛域名 SSL 证书的步骤。在此示例中，我们将使用 **Cloudflare** 作为 DNS 供应商。

1. 如果您尚未安装 acme.sh，请按照以下命令进行安装： 
   ```
   curl https://get.acme.sh | sh
   ```
   安装完成后，重新加载 shell 配置以使 acme.sh 可用：
   ```
   source ~/.bashrc
   ```

2. 确保已将 Cloudflare 的 API 密钥存储在环境变量中。您可以通过以下方式将其添加到您的 shell 配置文件（例如 `.bashrc` 或 `.bash_profile`）：
   ```
   export CF_Key="your_cloudflare_api_key"
   export CF_Email="your_cloudflare_email_address"
   ```
   然后，重新加载 shell 配置以使更改生效：
   ```
   source ~/.bashrc
   ```

3. 现在，使用 acme.sh 脚本为泛域名 `*.liuweiqing.top` 申请证书。请注意，此命令还包括根域名 `liuweiqing.top`：
   ```
   acme.sh --issue --dns dns_cf -d '*.liuweiqing.top' -d 'liuweiqing.top'
   ```
   接下来这里应该会弹出让你提供一个邮箱的提示，我们需要手动输入（注册邮箱地址允许证书颁发机构在证书即将过期、需要续订或有其他重要信息时通知你。）
   ```
   acme.sh --register-account -m liuweiqing147@gmail.com
   ```
   接下来脚本将自动使用 Cloudflare API 更新 DNS 记录以验证域名所有权。

4. 证书生成后，您需要将证书和私钥安装到您的 Web 服务器。以下是一个 Nginx 示例：（证书路径根据自己的情况修改）
   ```
   acme.sh --install-cert -d '*.liuweiqing.top' -d 'liuweiqing.top' \
     --key-file /etc/cert/key.pem \
     --fullchain-file /etc/cert/fullchain.pem \
     --reloadcmd "sudo systemctl reload nginx"
   ```
   这将安装证书和私钥文件到指定的路径，并在证书更新时自动重新加载 Nginx。

5. 最后，将 SSL 证书和私钥的路径添加到您的 Web 服务器（例如 Nginx 或 Apache）配置文件中。以下是一个 Nginx 示例配置片段：
   ```
   ssl_certificate /etc/cert/fullchain.pem;
   ssl_certificate_key /etc/cert/key.pem;
   ```

6. 保存更改后，重新加载 Web 服务器以使更改生效：
   ```
   sudo systemctl reload nginx  # 对于 Nginx
   ```

acme.sh 默认会在证书到期前尝试自动更新证书。