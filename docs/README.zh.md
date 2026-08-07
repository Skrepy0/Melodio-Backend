# 🎵 Melodio Backend
[![License](https://img.shields.io/badge/License-Apache%202.0-pink.svg)](LICENSE)

[🌐English](../README.md) | 🇨🇳 中文

Melodio Backend 是一个为 [Melodio](https://github.com/Skrepy0/Melodio)
移动端应用提供音乐搜索、歌单解析等的后端服务。它基于 [musicdl](https://github.com/CharlesPikachu/musicdl)
构建，支持查询多个主流音乐平台。

---

## ✨ 核心特性

- 🔍 **多平台聚合搜索**  
  支持网易云、QQ音乐、酷狗、酷我、咪咕、Bilibili、蜻蜓FM等多个音乐源。

- 📡 **实时流式响应 (SSE)**  
  搜索结果分批推送，客户端无需等待全部完成即可展示，缓解了musicdl搜索慢的问题。

- 📋 **歌单解析**  
  通过链接解析各平台歌单，支持批量获取歌曲信息。

- 🔐 **安全签名机制**  
  基于 HMAC-SHA256 的请求签名，防止篡改和重放攻击。

- ⚡ **高性能异步架构**  
  基于 FastAPI + asyncio，配合线程池执行阻塞 I/O，保证高并发下的稳定性。

---

## 🛠️ 技术栈

- **Python 3.12+**
- **FastAPI** – 现代 Web 框架
- **musicdl** – 多平台音乐数据聚合核心库
- **SSE (Server-Sent Events)** – 实时推送
- **Pydantic v2** – 数据验证与序列化
- **Uvicorn** – ASGI 服务器
- **HTTPX** – 异步 HTTP 客户端
- **Ruff** – 代码检查与格式化
- **pytest** – 单元测试

---

## 📦 项目结构

```
Melodio-Backend/
├── app/
│   ├── api/               # API 路由
│   │   └── v1/            # API 版本 v1
│   │       └── endpoints/ # 具体端点实现
│   ├── core/              # 核心配置与依赖（签名验证等）
│   ├── schemas/           # Pydantic 模型
│   ├── utils/             # 工具函数
│   └── __init__.py
├── tests/                 # 单元测试
├── .env.example           # 环境变量示例
├── .gitignore
├── LICENSE
├── main.py                # 应用入口
└── pyproject.toml         # 项目配置与依赖
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Skrepy0/Melodio-Backend.git
cd Melodio-Backend
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
# 或
.venv\Scripts\activate          # Windows
```

### 3. 安装依赖

项目使用 `pyproject.toml` 管理依赖，直接安装：

```bash
pip install -e .
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

```env
SECRET_KEY=your_secret_key_here   # 签名密钥，务必与客户端一致
```

### 5. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

---

## 🧪 测试

使用 pytest 运行测试：

```bash
# 运行所有测试
run test-all

# 仅运行 API 测试
run test-api
```

## 📄 开源协议

本项目基于 **Apache-2.0 license** 开源，详见 [LICENSE](../LICENSE) 文件。

---

## 🙏 致谢

- [musicdl](https://github.com/CharlesPikachu/musicdl) – 多平台音乐数据聚合库
- [FastAPI](https://fastapi.tiangolo.com/) – 高性能 Python Web 框架
- [Soundtrack](https://github.com/CharlesPikachu/musicdl/tree/master/examples/claudeai-modern-web-music-player) - 基于 musicdl 的现代化音乐 搜索 / 下载 / 播放器
