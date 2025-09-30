---
title: 【Nginx踩坑记】为什么 proxy_pass http://localhost:8055 会偶尔连不上？一次 IPv6 回环地址导致的坑
date: 2025-09-30
categories: tech
share: true
comments: true
author_profile: true
related: true
---


## 🧩 前言

在给 Directus 配 Nginx 反向代理时，我遇到了一个非常“玄学”的问题：

* 本机访问 `http://localhost:8055` 一切正常
* Nginx 配置了反代：

```nginx
location / {
    proxy_pass http://localhost:8055;
}
```

结果却是 —— **有时候能用，有时候就 502 Bad Gateway**，而且本机访问没问题，公网却总是打不开！
这到底是怎么回事？

---

## 🧠 原因解析：一切的根源在于“localhost”

很多人以为 `localhost` 就是 `127.0.0.1`，其实并不是。
在现代 Linux 系统中，它其实会解析出两个地址：

| 名称          | 含义        |
| ----------- | --------- |
| `127.0.0.1` | IPv4 回环地址 |
| `::1`       | IPv6 回环地址 |

而且，系统解析时的**优先级通常是 IPv6 在前**！

```bash
$ getent ahosts localhost
::1             STREAM     localhost
127.0.0.1       STREAM     localhost
```

这意味着：
当 Nginx 解析 `http://localhost:8055` 时，它**最先尝试的是 `::1:8055`**（IPv6 回环）。

---

## ⚠️ 问题来了：Directus 并没有监听 IPv6

Node.js 或很多 Web 服务默认只监听 IPv4，例如：

```bash
$ ss -lntp | grep 8055
LISTEN 0 128 127.0.0.1:8055 0.0.0.0:* users:(("node",pid=xxxx,fd=3))
```

可以看到，服务只监听了 `127.0.0.1`，**没有监听 `[::1]`**。

那么当 Nginx 优先去连接 `::1:8055` 时，就会发现端口没人监听，连接失败，于是你就会看到：

```
502 Bad Gateway
connect() failed (111: Connection refused) while connecting to upstream
```

---

## 🧪 为什么“本机能访问”，但“公网不行”？

这也是很多人感到迷惑的点。

本机直接访问时，curl 或浏览器可能会优先用 IPv4：

```bash
curl http://127.0.0.1:8055   # ✅ 正常
curl http://localhost:8055   # ✅ 正常（curl 默认优先 IPv4）
```

而 Nginx 不一样，它是严格按照 `getaddrinfo()` 返回的地址列表**顺序尝试**的，很多系统中 IPv6 优先，于是就“翻车”了。

公网访问时，Nginx 作为代理层失败，外面自然就访问不到了。

---

## 🔧 解决方案（4 种）

### ✅ 方案 1：最简单——写死 IPv4 地址

最直接、最推荐的解决办法就是不要用 `localhost`：

```nginx
location / {
    proxy_pass http://127.0.0.1:8055;
}
```

这样就不会有 IPv6 解析这一层的不确定性，问题立刻解决。

---

### ✅ 方案 2：让后端也监听 IPv6

如果你需要双栈支持（IPv4 + IPv6），可以让服务监听 `::`：

```js
server.listen(8055, '::');
```

这会让它同时监听 IPv4 和 IPv6（取决于系统配置），Nginx 无论解析到哪个都能连上。

---

### ✅ 方案 3：用 Unix Socket

如果前后端在同一台机器上，也可以直接走 Unix 套接字，完全绕开 IP：

```nginx
location / {
    proxy_pass http://unix:/run/directus.sock;
}
```

不过这种方式需要你把后端服务改成监听 socket 文件。

---

### ✅ 方案 4：修改地址选择策略（不推荐）

在 `/etc/gai.conf` 中调整地址优先级，让 IPv4 优先，也能解决，但这会影响全局网络行为，不建议作为首选。

---

## 🧰 补充：快速排查小技巧

当遇到 502 时，可以快速确认是不是这个 IPv6 坑：

```bash
# 看监听状态
ss -lntp | grep 8055

# 看 localhost 的解析顺序
getent ahosts localhost

# 手动测试 IPv6 回环是否能连上
curl http://[::1]:8055
```

如果 `[::1]:8055` 连不上，而 `127.0.0.1:8055` 能连，那 99% 就是这个问题。

---

## 📦 总结

这个坑非常常见，尤其是当你用 Node.js、Python Flask、Directus 等开发服务并用 Nginx 做反代时。
一句话总结：

> **`localhost` 并不等于 `127.0.0.1`，它可能解析为 IPv6 的 `::1`。如果后端没监听 IPv6，Nginx 就可能连不上！**

✅ 建议：**永远在 `proxy_pass` 中写明具体的回环地址：**

```nginx
proxy_pass http://127.0.0.1:8055;
```

这条“反代黄金法则”，可以帮你避开 90% 的“502 玄学问题”。

---

📌 **延伸阅读：**

* [RFC 6724 – Default Address Selection for IPv6](https://datatracker.ietf.org/doc/html/rfc6724)
* `man gai.conf` – 配置地址选择策略
* Nginx 官方文档：[proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)

---

✅ **一句话总结：**

> 当你用 `localhost` 做反代地址时，系统可能先解析成 IPv6 回环地址 `::1`，但后端没监听 IPv6 导致 Nginx 连接失败。解决办法是用 `127.0.0.1` 替代 `localhost`，或者让后端同时监听 IPv6。

