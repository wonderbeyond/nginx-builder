Nginx Builder
=============

Nginx 构建助手

## 依赖

- 库: build-essential zlib1g-dev libpcre3 libpcre3-dev libbz2-dev libssl-dev tar unzip
- 工具: rsync

## 构建并安装Nginx的步骤

#### 1. 在目标服务器上克隆该项目

```bash
git clone git@github.com:wonderbeyond/nginx-builder.git
cd nginx-builder
```

#### 2. 准备所有相关的包

```bash
./prepare-modules.py
```

#### 3. 执行构建并安装

```bash
./install.sh
```

## TODO

- 提供可选的下载方式, 加入失败重试机制
- 添加系统服务管理脚本
