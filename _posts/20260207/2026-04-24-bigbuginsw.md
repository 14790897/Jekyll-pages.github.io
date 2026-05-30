---
title: 记一次 PWA 域名迁移踩坑录：逃离 Service Worker 的“缓存黑洞”
date: 2026-04-24
categories:
  - tech
tags:
  - PWA
  - Service Worker
  - Cloudflare
---

最近修改了前端请求方式以及后端API接口以及之前更换过域名301永久重定向到新的域名，结果用户纷纷说前端报错，无法使用。经过排查发现，对于已经将网站作为 PWA 安装到本地的用户来说，问题尤为严重，因为 Service Worker 缓存了旧的请求逻辑和 API 地址，导致新的请求方式无法生效。

经过一番排查，我发现罪魁祸首是 PWA 的核心技术：**Service Worker (SW)**。

## 踩坑分析：为什么 301 重定向对老用户失效了？

在 PWA 架构中，导致全站 301 重定向失效的原因主要有两个：
1. **重定向会阻断 SW 更新**
   W3C 出于安全规范，不允许跨域更新 SW。当浏览器在后台尝试拉取新的 `sw.js` 以检查更新时，如果服务器返回了 301/302 状态码，浏览器会将其视为网络错误，并拒绝更新。这就导致老用户的旧 SW 陷入了“死锁”，持续无限期地运行旧版本。

2. **本地代理的绝对拦截**
   Service Worker 是运行在用户浏览器后台的“本地代理”。当老用户打开旧域名时，请求会被 SW 优先拦截。在这里我的 SW 有问题：优先读取本地 Cache（为了追求秒开），那么这个请求根本就不会发向真实网络，自然也到不了 Cloudflare。服务器上配置的 301 重定向对它来说形同虚设。


## 破局方案：借助 Cloudflare Worker 下发“自毁指令”

为了打破这个死锁，我们不能对 `sw.js` 进行重定向。相反，我们需要向老用户发送一个 **“自毁版”** 的 Service Worker，让它主动清理门户。

由于旧域名已经不再承载业务，我选择了使用 **Cloudflare Worker** 来精准接管旧域名的流量，并进行路由分发。

### 核心实现代码

在 CF Worker 中，拦截所有发往旧域名的请求。如果请求的是 `/sw.js`，就下发自毁脚本；如果是其他页面请求，则并行执行 301 重定向。

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetDomain = "你的新域名.com"; 

    // 1. 精准放行并下发自毁脚本
    if (url.pathname === '/sw.js') {
      const cleanupScript = `
        // 强制跳过等待，立即激活
        self.addEventListener('install', () => self.skipWaiting());

        self.addEventListener('activate', (e) => {
          e.waitUntil(
            // 清理旧域名下的所有缓存
            caches.keys().then(keys => Promise.all(keys.map(key => caches.delete(key))))
            // 注销旧版 SW
            .then(() => self.registration.unregister())
            .then(() => clients.claim())
            // 获取所有打开的页面，并强制重新导航
            .then(() => clients.matchAll({ type: 'window' }))
            .then(windowClients => {
              windowClients.forEach(client => {
                client.navigate(client.url);
              });
            })
          );
        });

        // 兜底策略：确保后续请求不再拦截，透传至网络
        self.addEventListener('fetch', (e) => {
          e.respondWith(fetch(e.request));
        });
      `;

      return new Response(cleanupScript, {
        headers: {
          'Content-Type': 'application/javascript',
          'Cache-Control': 'no-cache' 
        }
      });
    }

    // 2. 对其他常规请求执行 301 重定向，带上完整的路径和参数
    const destination = `https://${targetDomain}${url.pathname}${url.search}`;
    return Response.redirect(destination, 301);
  },
};
```

### 关键点解析：为什么要用 `client.navigate`？

在早期的测试中，我发现仅仅调用 `unregister()` 注销 SW 是不够的。因为当前屏幕上渲染的依然是最初拦截下来的旧缓存页面，同时sw是自毁脚本。用户必须手动按 `F5` 刷新一次，才能真正触发网络请求走到新域名。

为了做到对用户打扰最小的**无缝迁移**，加入了 `client.navigate(client.url)`。它的运作流程如下：
1. 老用户打开旧页面，看到一闪而过的旧缓存。
2. 后台默默下载了自毁脚本，瞬间清空缓存并注销 SW。
3. 脚本强制命令当前页面“重新加载”。
4. **由于此时 SW 已死，这个刷新请求畅通无阻地打向了真正的外网。**
5. CF Worker 捕获到这个普通页面请求，返回 301，浏览器瞬间跳转到新域名。

这一套组合拳完美避开了由于单纯 `Maps` 可能引发的无限刷新死循环，因为重定向像安全气囊一样把用户弹射到了全新的运行环境中。

## 现实与妥协：桌面端 PWA 的“跨域死刑”

网页端的体验虽然修复完美，但在电脑桌面或手机桌面上，那些 **已经安装为独立 App**  的旧版本依然遇到了问题：打开后直接白屏，或是报错退出。

这并不是代码写错了，而是触碰了 PWA 的底层安全红线—— **作用域限制（Scope）**。

安装在用户本地的 App 是死死绑定在旧域名的 `manifest.json` 上的。当我们用 `Maps` + 301 强行将这个 App 的内核指向一个全新域名时，浏览器触发了跨站劫持防护，强行切断了渲染。

**这也是 PWA 开发者必须接受的现实：** 没有任何技术手段能在后台悄无声息地把用户设备上的 A 域名 App 替换成 B 域名 App。对于 PWA 而言，更换域名等于一次“转世重生”。旧的 App 躯壳必然作废，只能通过原域名的瘫痪，或者在新页面引导老用户，让他们重新安装新域名的版本。

## 总结

给一个前端 PWA 项目换域名，远比给传统服务端渲染网站换域名要复杂。Service Worker 赋予了 Web 应用离线访问的能力，但也像一个忠诚过头的卫士，在关键时刻可能会阻断你的迁移路线。

如果你也面临类似的架构调整，务必提前规划好旧版 SW 的“后事”，合理利用云原生边缘节点（如 CF Worker）进行精确的流量控制，才能最大程度地减少老用户的流失。

