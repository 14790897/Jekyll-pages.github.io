---
title: 如何把Ubuntu上的程序打包成docker文件？
date: 2023-05-18
categories: Linux
---

## 如何把Ubuntu上的程序打包成docker文件？

要将 Ubuntu 上的程序打包成 Docker 镜像，您需要创建一个 Dockerfile，该文件描述了如何在 Docker 容器内部安装和设置程序。下面是一般的步骤：

1. **创建一个 Dockerfile**

首先，创建一个名为 `Dockerfile` 的文件。您可以在任何文本编辑器中完成此操作，包括 Vim、Nano 或者是 GUI 类型的文本编辑器。

2. **指定基础镜像**

在 Dockerfile 的顶部，指定您要使用的基础镜像。由于程序运行在 Ubuntu 上，您可能会选择一个 Ubuntu 镜像作为基础。例如：

```Dockerfile
FROM ubuntu:20.04
```

3. **安装必要的软件包**

使用 `RUN` 指令安装程序所需的任何依赖项。例如，如果您的程序需要 Python 和 pip，您可能会添加如下指令：

```Dockerfile
RUN apt-get update && apt-get install -y python3 python3-pip
```

4. **添加您的程序**

使用 `COPY` 或 `ADD` 指令将您的程序添加到镜像中。例如，如果您的程序在当前目录的 `app/` 子目录中，您可以添加如下指令：

```Dockerfile
COPY ./app /app
```

5. **配置程序的运行环境**

您可能需要配置环境变量、工作目录或者是其他的运行环境。例如，设置工作目录和环境变量：

```Dockerfile
WORKDIR /app
ENV MODE production
```

6. **设置默认命令**

最后，使用 `CMD` 指令设置启动容器时要运行的默认命令。例如，如果您的程序是一个 Python 脚本，您可能会添加如下指令：

```Dockerfile
CMD ["python3", "your_script.py"]
```

完成以上步骤后，您的 Dockerfile 可能看起来像这样：

```Dockerfile
FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip

COPY ./app /app

WORKDIR /app
ENV MODE production

CMD ["python3", "your_script.py"]
```

7. **构建 Docker 镜像**

在 Dockerfile 所在的目录运行以下命令，构建您的 Docker 镜像：

```bash
docker build -t your_image_name .
```

现在，您可以通过运行以下命令来启动您的程序：

```bash
docker run your_image_name
```

注意，以上只是一个简单的例子，实际情况会根据您的程序的具体需求进行调整。

## docker的程序可以像systemd的程序一样后台运行，开机自启动吗？

是的，Docker 容器确实可以像 systemd 的服务一样在后台运行，并设置为开机自启动。这主要通过两种方式实现：

1. **使用 Docker 自带的 `restart` 策略**：在运行容器时，可以使用 `--restart` 标志来设置 Docker 的自动重启策略。例如，`docker run --restart=always -d your_image` 将启动一个在 Docker 服务启动时自动启动的容器，即使容器退出，Docker 也会尝试重新启动它。

2. **使用 systemd 管理 Docker 容器**：另一种方法是将 Docker 容器作为 systemd 服务运行。这需要创建一个 systemd 服务文件，其中描述了如何启动和停止 Docker 容器。然后，可以使用 `systemctl` 命令来启动、停止和检查容器的状态，以及设置容器在启动时自动启动。

以下是一个简单的 systemd 服务文件示例，该文件将 Docker 容器作为服务运行：

```ini
[Unit]
Description=My Docker Application
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a my_container
ExecStop=/usr/bin/docker stop -t 2 my_container

[Install]
WantedBy=default.target
```

在这个例子中，服务依赖于 `docker.service`，因此 Docker 服务会在这个服务之前启动。在 Docker 服务运行之后，`ExecStart` 指令将启动 Docker 容器，而 `ExecStop` 指令将停止它。`Restart=always` 指令告诉 systemd 在服务退出时总是尝试重新启动服务。

然后，你可以使用 `systemctl enable your_service` 命令来设置这个服务在系统启动时自动启动，其中 `your_service` 是你的 systemd 服务文件的名称。

请注意，这只是一个简单的示例，实际的 systemd 服务文件可能需要根据你的需求进行调整。另外，这需要在主机上具有管理员权限，并且主机需要运行 systemd。

## Dockerfile如何运行？如何让用户输入参数？

运行 Dockerfile 以创建 Docker 镜像的命令是 `docker build`。例如，假设你的 Dockerfile 位于当前目录，你可以使用以下命令构建 Docker 镜像：

```bash
docker build -t your_image_name .
```

`-t` 标志用于给你的镜像指定一个名字，`.` 指定了 Dockerfile 所在的目录（在这个例子中，是当前目录）。

关于在 Dockerfile 中允许用户输入参数，Docker 提供了 `ARG` 和 `ENV` 两种机制来处理参数和环境变量。

`ARG` 可以在构建过程中使用，可以使用 `--build-arg <varname>=<value>` 标志传递给 `docker build` 命令，例如：

```bash
docker build --build-arg VARNAME=value -t your_image_name .
```

在 Dockerfile 中，你可以使用 ARG 指令来定义一个变量：

```Dockerfile
ARG VARNAME
RUN echo $VARNAME
```

`ENV` 可以在构建过程和运行容器时使用。你可以在 Dockerfile 中使用 `ENV` 指令来设置环境变量：

```Dockerfile
ENV VARNAME default_value
```

然后，你可以在运行容器时通过 `-e` 标志来覆盖这些环境变量：

```bash
docker run -e "VARNAME=value" your_image_name
```

这些机制都可以帮助你在 Docker 构建和运行过程中处理参数。
