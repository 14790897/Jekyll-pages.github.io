---
title: iptables、ip rule、ip route 的分工与执行顺序
date: 2025-12-13
categories: tech
share: true
comments: true
author_profile: true
related: true
tags: [Linux, 网络, iptables, ip rule, ip route, 排障]
---


很多网络问题之所以难排（端口不通、转发失败、多出口分流不生效、NAT 看起来“没做”），根本原因是把三件事混在一起了：

* **iptables**：对“包”做动作（放行/拒绝、NAT、打标、改字段）
* **ip rule**：对“流量类别”做分流（决定查哪张路由表）
* **ip route**：在“某张路由表”里算路由（下一跳、出接口、源地址等）

这篇文章用最少概念把三者的职责边界讲清楚，并给出三条常见路径的**实际执行顺序**与**排障检查顺序**（附命令）。

---

## 目录

1. 三者分别负责什么
2. 为什么需要拆成三类工具
3. 三条典型路径的执行顺序（入站、本机出站、转发）
4. 一套可复制的排障命令清单
5. 常见误区与快速定位方法

---

## 1. 三者分别负责什么

### 1.1 iptables：包怎么处理

iptables 属于 netfilter 框架，关注的是“包进来/出去/转发过程中怎么处理”。

典型用途：

* 放行/阻断：ACCEPT/DROP/REJECT（filter 表）
* DNAT/SNAT/MASQUERADE（nat 表）
* 打 mark（mangle 表），供策略路由分流使用

一句话：**iptables 决定包“能不能过、要不要改、要不要打标”。**

---

### 1.2 ip rule：这类流量查哪张路由表

当你有多出口、多 VPN、专线/公网分流时，一张 main 路由表不够用。策略路由通过 **ip rule** 把不同流量映射到不同路由表。

常见匹配维度：

* `from`：按源地址/源网段
* `to`：按目的网段
* `fwmark`：按防火墙标记（常见：iptables MARK + ip rule fwmark）
* 其他：入接口/用户等（视内核与发行版支持）

一句话：**ip rule 决定“用哪张表算路”。**

---

### 1.3 ip route：具体怎么走

路由表本身由 ip route 管，决定实际下一跳与出接口。

典型用途：

* 配默认路由：`default via ... dev ...`
* 配静态路由：`10.10.0.0/16 via ...`
* 查看某表：`ip route show table 100`
* 直接问内核“这包怎么走”：`ip route get ...`

一句话：**ip route 给出“算路结果”：走哪个接口、下一跳是谁。**

---

## 2. 为什么要拆成三类

拆开以后每层只解决一个问题：

* **iptables** 适合按“五元组/连接状态/端口/协议”表达安全与改包逻辑
* **ip rule** 适合按“流量类别”做策略分流（多路由表的选择器）
* **ip route** 专注于“路由算法与路由表内容”（最匹配路由、度量、下一跳）

拆分带来的好处是可组合。例如典型多出口方案：

1. iptables 在 mangle 表给某类包打 `mark=1`
2. ip rule 匹配 `fwmark 1`，让它查 table 100
3. ip route 在 table 100 给出专用出口网关

---

## 3. 执行顺序到底是什么（按场景）

下面给出三条最常见路径。你只要先判断自己属于哪条路径，排障会快很多。

### 3.1 外部进来，目标是本机服务（INPUT 路径）

示例：外部访问本机的 22/80/443。

**简化执行顺序：**

```
网卡收包
  ↓
PREROUTING（raw → mangle → nat）
  ↓
路由决策：ip rule → 选表；ip route → 查表
  ↓
INPUT（mangle → filter）
  ↓
本机进程（socket）
```

**关键点：**

* 如果你做了端口映射（DNAT），通常发生在 `nat/PREROUTING`
* 真正决定“能否访问到本机服务”的常在 `filter/INPUT`（当然也可能被其他链影响）

---

### 3.2 本机发出访问（OUTPUT 路径）

示例：在服务器上 `curl` 外网，或访问其他网段。

**简化执行顺序：**

```
本机进程发包
  ↓
OUTPUT（raw → mangle → nat → filter）
  ↓
路由决策：ip rule → ip route
  ↓
POSTROUTING（mangle → nat）
  ↓
发出
```

**关键点：**

* 本机出站的策略分流，常靠 `mangle/OUTPUT` 打 mark，然后 `ip rule` 按 mark 选表
* SNAT/MASQUERADE 常在 `nat/POSTROUTING`

---

### 3.3 外部进来，需要经过本机转发（FORWARD 路径）

示例：你机器是网关/旁路由/宿主机转发容器、K8s 节点转发等。

**简化执行顺序：**

```
网卡收包
  ↓
PREROUTING（raw → mangle → nat）
  ↓
路由决策：ip rule → ip route
  ↓
FORWARD（mangle → filter）
  ↓
POSTROUTING（mangle → nat）
  ↓
转发出接口
```

**关键点：**

* DNAT（端口映射）通常仍在 `nat/PREROUTING`
* 是否允许转发，通常看 `filter/FORWARD`
* 出口改源地址（SNAT/MASQ）通常在 `nat/POSTROUTING`
* 别忘了内核转发开关：`net.ipv4.ip_forward=1`

---

## 4. 一套可复制的排障命令清单（强烈建议按顺序跑）

### 4.1 先看策略路由与路由表

```bash
ip rule
ip route show table main
# 如有自定义表（示例 100/200）
ip route show table 100
ip route show table 200
```

### 4.2 直接问内核“这包会怎么走”（最有效）

```bash
# 最基本：只给目的
ip route get 8.8.8.8

# 指定源地址（多出口时很关键）
ip route get 8.8.8.8 from 192.0.2.10
```

若你是入站排障（知道入接口），可以配合链路信息与抓包进一步确认，但“route get”通常能先把方向判断对。

### 4.3 看 iptables 规则与命中计数（建议都带 -n -v 和行号）

```bash
# filter（放行/拒绝）
iptables -L -n -v --line-numbers

# nat（DNAT/SNAT/MASQ）
iptables -t nat -L -n -v --line-numbers

# mangle（mark、TOS/DSCP 等）
iptables -t mangle -L -n -v --line-numbers
```

### 4.4 转发场景再确认内核开关

```bash
sysctl net.ipv4.ip_forward
```

---

## 5. 常见误区（非常高频）

### 误区 1：只看 filter 表，不看 nat/mangle

端口映射、出网伪装、多出口打标都不在 filter 表里。排 NAT/分流时必须看：

* `iptables -t nat ...`
* `iptables -t mangle ...`

---

### 误区 2：以为“路由就是 ip route”，忽略 ip rule

只要你看到系统里有非默认的 `ip rule`（例如按 from/fwmark 分流），就必须明确：
**main 表并不一定参与决策**，实际查表可能是 100/200 等自定义表。

---

### 误区 3：只排 INPUT，忘了 OUTPUT/FORWARD

* “本机访问不通”优先看 OUTPUT
* “别人经过你转发不通”优先看 FORWARD
  只盯着 INPUT 往往会浪费时间。

---

### 误区 4：IPv6 没看

很多“规则都配了但不生效”，原因是流量走了 IPv6。需要同时确认：

```bash
ip -6 rule
ip -6 route
ip6tables -L -n -v --line-numbers
```

---

## 结语：用一句话记住顺序

当涉及路由选择时，大体可以按这个心智模型：

* **先（可能）iptables 改包/打标**
* **再 ip rule 选表**
* **再 ip route 算路**
* **最后（可能）iptables 做 SNAT/MASQ**
