---
title: 一个很多人不知道的 Android 存储误区：`rm -rf` 并不一定会释放空间
date: 2025-12-19
categories: tech
tags: [android, storage, adb, rm, rm-rf, miui, hyperos]
header:
  overlay_image: https://images.unsplash.com/photo-1694622343912-9b6d963cea3f?q=80&w=1172&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
  overlay_filter: 0.5
  teaser: https://images.unsplash.com/photo-1694622343912-9b6d963cea3f?q=80&w=1172&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D
  caption: "Photo credit: [Unsplash](https://unsplash.com)"
---

在使用 ADB 清理 Android 手机存储时，很多人都会下意识地认为：

> **只要我用 `adb shell rm -rf` 把文件夹删掉了，空间就一定会立刻释放。**

**但在实际使用中，这个认知在现代 Android（尤其是 MIUI / HyperOS）上是错误的。**

我最近就踩到了这个坑。

---

## 一、真实场景：文件删了，空间却没回来

我在清理手机存储时，执行了类似命令：

```bash
adb shell rm -rf "/sdcard/Download/某相册目录"
```

命令没有报错，目录也确实消失了。
但问题是：

- 系统显示的可用空间 **几乎没有变化**
- `df -h` 看到的剩余空间也不对

这时候很多人会开始怀疑：

- 是不是 `du` 不准？
- 是不是需要 `fstrim`？
- 是不是系统统计延迟？

**其实都不是根本原因。**

---

## 二、真正的原因：相册“回收站”机制

在 MIUI / HyperOS 等系统中：

- 系统相册（或第三方相册 App）
- 会**监听媒体文件的删除行为**
- 当你删除照片 / 视频时：

  - 文件不会立刻物理删除
  - 而是被**移动或接管到「相册回收站」**

关键点是：

> **回收站里的文件仍然占用真实存储空间。**

即使你是通过：

- 文件管理器删除
- ADB `rm -rf`
- 甚至某些脚本删除

只要删除的是**媒体文件**，就可能被相册接管。

---

## 三、为什么 ADB 看不到这些文件？

这是 Android 11+ 的另一个关键变化：

- Scoped Storage（分区存储）
- MediaStore 接管媒体文件生命周期
- 相册回收站目录：

  - 通常位于 **App 私有目录**
  - 非 root 的 ADB **不可访问**

所以你会看到：

- `/sdcard` 下面文件确实没了
- 但空间就是不释放

---

## 四、正确、彻底释放空间的方法

### ✅ 方法一（最推荐）

打开系统 **相册 App → 回收站 → 清空回收站**

这是：

- 官方路径
- 立即生效
- 不会破坏系统状态

---

## 五、总结

**一句话总结这个误区：**

> 在现代 Android 系统中，`rm -rf` 只能删除你“看到的文件”，
> **并不能保证释放你“占用的空间”。**

如果你发现：

- 文件已经删了
- 但空间一直没回来

**第一时间应该去检查：相册的回收站。**
