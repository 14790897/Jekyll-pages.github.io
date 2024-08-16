---
title: 安卓(无root) 从零安装docker
date: 2024-08-16
categories: tech
share: true
comments: true
author_profile: true
related: true
---

1. 在您的安卓设备上打开 Termux。

2. 通过运行以下命令更新和升级软件包：

   ```bash
   pkg update -y && pkg upgrade -y
   ```

3. 运行以下命令安装必要的依赖：

   ```bash
   pkg install qemu-utils qemu-common qemu-system-x86_64-headless wget -y
   ```

4. 创建一个独立的目录：

   ```bash
   mkdir alpine && cd alpine
   ```

5. 下载 Alpine Linux 3.19（经过虚拟化优化）的 ISO 文件：

   ```bash
   wget http://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-virt-3.19.1-x86_64.iso
   ```

6. 创建磁盘（注意：它实际上不会占用 5GB 的空间，而是大约 500-600MB）：

   ```bash
   qemu-img create -f qcow2 alpine.img 5G
   ```

7. 启动虚拟机（-m 1024 指使用了 1024MB 的内存）：

   ```bash
   qemu-system-x86_64 -machine q35 -m 1024 -smp cpus=2 -cpu qemu64 -drive if=pflash,format=raw,read-only=on,file=$PREFIX/share/qemu/edk2-x86_64-code.fd -netdev user,id=n1,dns=8.8.8.8,hostfwd=tcp::2222-:22 -device virtio-net,netdev=n1 -cdrom alpine-virt-3.19.1-x86_64.iso -nographic alpine.img
   ```

8. 使用用户名 `root` 登录（没有密码）。

9. 设置网络（按回车键使用默认设置）：

   ```bash
   localhost:~# setup-interfaces
    Available interfaces are: eth0.
    Enter '?' for help on bridges, bonding and vlans.
    Which one do you want to initialize? (or '?' or 'done') [eth0]
    Ip address for eth0? (or 'dhcp', 'none', '?') [dhcp]
    Do you want to do any manual network configuration? [no]
   ```

   然后运行：

   ```bash
   ifup eth0
   ```

10. 创建一个应答文件以加快安装过程：

    ```bash
    wget https://raw.githubusercontent.com/14790897/docker-in-termux-cn/master/answerfile
    ```

    > **注意：** 如果您看到类似于 `wget: bad address 'gist.githubusercontent.com'` 的错误，请运行以下命令：
    >
    > ```bash
    > echo -e "nameserver 192.168.1.1\nnameserver 1.1.1.1" > /etc/resolv.conf
    > ```

11. 修补 `setup-disk` 以在启动时启用串口控制台输出：

    ```bash
    sed -i -E 's/(local kernel_opts)=.*/\1="console=ttyS0"/' /sbin/setup-disk
    ```

12. 运行安装设置将系统安装到磁盘：

    ```bash
    setup-alpine -f answerfile
    ```

13. 安装完成后，关闭虚拟机（使用命令 `poweroff`）。

14. 再次启动但不加载 CD-ROM：
    ```bash
    qemu-system-x86_64 -machine q35 -m 1024 -smp cpus=2 -cpu qemu64 -drive if=pflash,format=raw,read-only=on,file=$PREFIX/share/qemu/edk2-x86_64-code.fd -netdev user,id=n1,dns=8.8.8.8,hostfwd=tcp::2222-:22 -device virtio-net,netdev=n1 -nographic alpine.img
    ```

### 可以创建脚本，快速启动

A - 创建脚本 `run_qemu.sh`：

```bash
nano run_qemu.sh
```

在文本编辑器中，写入以下内容：

```bash
#!/bin/bash
qemu-system-x86_64 -machine q35 -m 1024 -smp cpus=2 -cpu qemu64 -drive if=pflash,format=raw,read-only=on,file=$PREFIX/share/qemu/edk2-x86_64-code.fd -netdev user,id=n1,dns=8.8.8.8,hostfwd=tcp::2222-:22 -device virtio-net,netdev=n1 -nographic alpine.img
```

保存并关闭文件。在 nano 中，您可以按 `Ctrl+X`，然后按 `Y` 确认保存，再按回车确认文件名。

B - 使用 `chmod` 命令赋予脚本可执行权限：

```bash
chmod +x run_qemu.sh
```

C - 运行脚本：

```bash
./run_qemu.sh
```

15. 更新系统并安装 Docker：

    ```bash
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

    apk update && apk add docker
    ```

16. 启动 Docker：

    ```bash
    service docker start
    ```

17. 设置 Docker 开机自启：

    ```bash
    rc-update add docker
    ```

18. 检查 Docker 是否成功安装：
    ```bash
    docker run hello-world
    ```

## 一些有用的快捷键

- `Ctrl+a x`: 退出仿真
- `Ctrl+a h`: 切换 QEMU 控制台
