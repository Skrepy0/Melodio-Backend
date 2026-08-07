# 🎵 Melodio Backend
[![License](https://img.shields.io/badge/License-Apache%202.0-pink.svg)](LICENSE)

🌐English | [🇨🇳 中文](./docs/README.zh.md)

Melodio Backend is a backend service that provides music search, playlist parsing, and more for the [Melodio](https://github.com/Skrepy0/Melodio) mobile application. It is built on top of [musicdl](https://github.com/CharlesPikachu/musicdl) and supports querying multiple mainstream music platforms.

---

## ✨ Key Features

- 🔍 **Multi‑platform Aggregated Search**  
  Supports NetEase, QQ Music, Kugou, Kuwo, Migu, Bilibili, Qingting FM, and more.

- 📡 **Real‑time Streaming (SSE)**  
  Search results are pushed in batches, allowing the client to display partial results without waiting for all sources to finish – solving the slow search issue of musicdl.

- 📋 **Playlist Parsing**  
  Parse playlists from various platforms via URLs and retrieve song information in bulk.

- 🔐 **Secure Signature Mechanism**  
  HMAC‑SHA256 based request signing to prevent tampering and replay attacks.

- ⚡ **High‑performance Async Architecture**  
  Built with FastAPI + asyncio, combined with a thread pool for blocking I/O, ensuring stability under high concurrency.

---

## 🛠️ Tech Stack

- **Python 3.12+**
- **FastAPI** – Modern web framework
- **musicdl** – Core multi‑platform music data aggregation library
- **SSE (Server‑Sent Events)** – Real‑time push
- **Pydantic v2** – Data validation and serialization
- **Uvicorn** – ASGI server
- **HTTPX** – Async HTTP client
- **Ruff** – Linting and formatting
- **pytest** – Unit testing

---

## 📦 Project Structure

```
Melodio-Backend/
├── app/
│   ├── api/               # API routes
│   │   └── v1/            # API version v1
│   │       └── endpoints/ # Endpoint implementations
│   ├── core/              # Core config & dependencies (signature verification, etc.)
│   ├── schemas/           # Pydantic models
│   ├── utils/             # Utility functions
│   └── __init__.py
├── tests/                 # Unit tests
├── .env.example           # Environment variables example
├── .gitignore
├── LICENSE
├── main.py                # Application entry point
└── pyproject.toml         # Project config & dependencies
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Skrepy0/Melodio-Backend.git
cd Melodio-Backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
# or
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

The project uses `pyproject.toml` for dependency management. Install with:

```bash
pip install -e .
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and edit:

```bash
cp .env.example .env
```

```env
SECRET_KEY=your_secret_key_here   # Signing key, must match the client
```

### 5. Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for the auto‑generated API documentation.

---

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
run test-all

# Run only API tests
run test-api
```

---

## 📄 License

This project is licensed under the **Apache‑2.0 License** – see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgements

- [musicdl](https://github.com/CharlesPikachu/musicdl) – Multi‑platform music data aggregation library
- [FastAPI](https://fastapi.tiangolo.com/) – High‑performance Python web framework
- [Soundtrack](https://github.com/CharlesPikachu/musicdl/tree/master/examples/claudeai-modern-web-music-player) - A modern web-based music search / download / player built on top of musicdl