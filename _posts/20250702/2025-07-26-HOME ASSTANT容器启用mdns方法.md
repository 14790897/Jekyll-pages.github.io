---
title: HOME ASSTANT容器启用mdns方法
date: 2025-07-26
categories: tech
share: true
comments: true
author_profile: true
related: true
---


## 🧠 背景简述（为什么默认不能解析 `.local`）

1. **容器使用的 musl libc（如 Alpine）不支持 `libnss-mdns` 和 `nsswitch.conf` 的 mdns hook**，所以：

   * 即使主机能 ping `*.local`，容器里仍然解析失败。

2. **mDNS 广播发现与 DNS 解析是两个过程：**

   * `avahi-browse` 能发现设备。
   * 但 `ping`、`esphome` 等实际是调用 `getaddrinfo()`，依赖 **DNS 服务器解析 `.local` 主机名**。

---

## ✅ 目标

让容器（如 Home Assistant / ESPHome）通过 DNS 查询 `.local` 主机名时，**返回正确 IP 地址**（例如 `myesp32c3.local` → `192.168.0.109`）。

---

## 🧰 总体解决方案：使用 `dnsmasq + avahi-browse` 实现 `.local` 到 IP 的同步解析

### 步骤 1：安装所需组件

```bash
sudo apt install avahi-daemon avahi-utils dnsmasq
```

---

### 步骤 2：配置 dnsmasq 支持 `.local` 域名

创建或编辑 `/etc/dnsmasq.d/mdns.conf`：

```ini
# 让 dnsmasq 监听本地
port=53
listen-address=127.0.0.1

# 本地域名设置
domain=local
local=/local/

# 不读 /etc/hosts（我们将手动生成 hosts）
no-hosts
addn-hosts=/etc/mdns-hosts.list
```

然后创建空文件：

```bash
sudo touch /etc/mdns-hosts.list
sudo chmod 644 /etc/mdns-hosts.list
```

---

### 步骤 3：编写自动同步脚本

```bash
➜  ~ avahi-browse -rt _esphomelib._tcp
+ enp1s0 IPv4 myesp32c3-sht30                               _esphomelib._tcp     local
+ enp1s0 IPv4 voc-myesp32c3                                 _esphomelib._tcp     local
= enp1s0 IPv4 myesp32c3-sht30                               _esphomelib._tcp     local
   hostname = [myesp32c3-sht30.local]
   address = [192.168.0.109]
   port = [6053]
   txt = ["friendly_name=SHT30 ESP32-C3 Sensor" "version=2025.7.2" "mac=34cdb0a7bc00" "platform=ESP32" "board=airm2m_core_esp32c3" "network=wifi"]
= enp1s0 IPv4 voc-myesp32c3                                 _esphomelib._tcp     local
   hostname = [voc-myesp32c3.local]
   address = [192.168.0.100]
   port = [6053]
   txt = ["friendly_name=VOC-CO2-HCHO ESP32-C3 Sensor" "version=2025.7.2" "mac=34cdb0b4eab0" "platform=ESP32" "board=airm2m_core_esp32c3" "network=wifi"]
```

保存如下脚本为 `/usr/local/bin/update-mdns-hosts.sh`：

📜 **脚本内容**（去括号+更新文件+重启 dnsmasq）：

```bash
#!/bin/bash

set -e

echo "🔍 正在通过 avahi-browse 扫描 mDNS 设备..."

TMPFILE="/tmp/mdns-hosts.list"
> "$TMPFILE"

# 使用 avahi-browse 扫描并提取 IP 和主机名
avahi-browse -rt _esphomelib._tcp 2>/dev/null |
awk '
  $1 == "hostname" { name = $3 }
  $1 == "address" {
    gsub(/\[|\]/, "", $3);  # 去除IP方括号
    ip = $3;
    gsub(/\[|\]/, "", name); # 去除主机名方括号
    if (name && ip) print ip, name;
    name = ""; ip = "";
  }
' |
sort -u |
while read -r ip host; do
  if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "✅ 添加映射：$host → $ip"
    echo "$ip $host" >> "$TMPFILE"
  else
    echo "⚠️ 跳过无效行: $ip $host"
  fi
done

# 检查是否有有效结果
if [[ -s "$TMPFILE" ]]; then
  echo "📝 正在更新 /etc/mdns-hosts.list ..."
  sudo cp "$TMPFILE" /etc/mdns-hosts.list

  echo "🔁 重启 dnsmasq ..."
  sudo systemctl restart dnsmasq

  echo "✅ 更新完成！"
else
  echo "⚠️ 未获取到任何有效 .local 设备，未更新文件"
fi
```

赋予可执行权限：

```bash
sudo chmod +x /usr/local/bin/update-mdns-hosts.sh
```

---

### 步骤 4：运行一次确认结果

```bash
sudo /usr/local/bin/update-mdns-hosts.sh
```

测试是否成功：

```bash
dig @127.0.0.1 myesp32c3.local +short
ping myesp32c3.local
```

---

### 步骤 5：让容器使用主机的本地 DNS 服务

修改容器 DNS 解析配置，确保 `/etc/resolv.conf` 包含：

```
nameserver 127.0.0.1
```

**或者**，在 docker compose 中设置：

```yaml
services:
  homeassistant:
    network_mode: host
    dns:
      - 127.0.0.1
```

---

### 可选：开机自启或定时任务

添加 crontab 每分钟刷新一次：

```bash
sudo crontab -e
```

加入：

```
* * * * * /usr/local/bin/update-mdns-hosts.sh >/dev/null 2>&1
```

或者

## 可选：设置定时任务自动更新 mDNS 映射

使用 `systemd` 定时执行（推荐）：

```bash
sudo nano /etc/systemd/system/mdns-sync.service
```

填入：

```ini
[Unit]
Description=Update mDNS host entries for dnsmasq

[Service]
Type=oneshot
ExecStart=/usr/local/bin/update-mdns-hosts.sh
```

定时器配置：

```bash
sudo nano /etc/systemd/system/mdns-sync.timer
```

内容：

```ini
[Unit]
Description=Run mDNS sync every 30s

[Timer]
OnBootSec=30
OnUnitActiveSec=30
Unit=mdns-sync.service

[Install]
WantedBy=timers.target
```

启用并启动：

```bash
sudo systemctl daemon-reexec
sudo systemctl enable --now mdns-sync.timer
```

---

## 🧪 效果验证

你现在应该可以在容器内运行：

```bash
ping myesp32c3.local
esphome logs myesp32c3.local
```

**不再报错 `Unknown host` 或 `cannot resolve .local`。**