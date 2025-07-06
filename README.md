# 🚀 Slack Collaboration Tool Clone

A modern, full-stack Slack-like collaboration platform built with cutting-edge technologies, featuring real-time messaging, video calls, file sharing, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0.2-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7.2-red?logo=redis&logoColor=white)](https://redis.io/)
[![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-orange?logo=minio&logoColor=white)](https://min.io/)
[![LiveKit](https://img.shields.io/badge/LiveKit-WebRTC-blueviolet?logo=livekit&logoColor=white)](https://livekit.io/)

[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)


---

## 📋 Table of Contents

* [✨ Features](#-features)
* [🗼 App Preview](#-app-preview)
* [🛠️ Tech Stack](#-tech-stack)
* [🏗️ Architecture](#-architecture)
* [💄 Database Schema](#-database-schema)
* [📚 Documentation](#-documentation)
* [🔌 API Reference](#-api-reference)
* [🚀 Quick Start](#-quick-start)
* [🐳 Docker Installation](#-docker-installation)
* [🔧 Development Setup](#-development-setup)
* [🧪 Testing](#-testing)
* [📦 Deployment](#-deployment)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)
* [❤️ Acknowledgements](#-acknowledgements)


---


## ✨ Features

> 🧩 Built to emulate the core experiences of modern collaboration tools like Slack, Zoom, and Notion — all in one workspace.

### ⚙️ Core Functionality Overview

| 🔧 Feature                 | 📝 Description                                                             |
| -------------------------- | -------------------------------------------------------------------------- |
| 💬 **Live Chat**           | Real-time messaging using WebSockets with channel-based threads.           |
| 📞 **Video Calls**         | Seamless group video and audio calling using **LiveKit** integration.      |
| 📂 **File Sharing**        | Upload and share files securely via **MinIO**, with drag-and-drop support. |
| 🧵 **Message Threads**     | Keep discussions focused using threaded replies and reactions.             |
| 😊 **Emoji Reactions**     | React with emojis to lighten up conversations.                             |
| 🔔 **Notifications**       | Real-time desktop and in-app notifications for mentions, messages, etc.    |
| 🛡️ **JWT Authentication** | Secure login/signup flows using access tokens and refresh tokens.          |
| 🔐 **Permissions**         | Fine-grained role-based access and private/public channel toggles.         |

---

### 🧠 Visual Feature Map

```mermaid
graph TD
  A[User] -->|Login/Register| B[Auth Service]
  A -->|Join Channel| C[Channel Service]
  A -->|Send Message| D[Message Service]
  A -->|Start Video Call| E[Video Service]
  A -->|Upload File| F[File Service]
  B --> G[MongoDB]
  C --> G
  D --> G
  F --> H[MinIO]
  E --> I[LiveKit]
```

---

## 🗼️ App Preview

### Login 
![Dashboard](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/1.png)

### Registration
![Channel Chat](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/2.png)

### Dashboard Overview
![Video Call](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/3.png)

### Messaging & Threading
![Message Threading](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/6.png)

### Call Preview
![Call Preview](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/4.png)

### Video Call
![Video Call](https://fmzqhgyfpkifsbymzdoy.supabase.co/storage/v1/object/public/portfolio/collaboration-tool-slack-clone/5.png)

---

## 🛠️ Tech Stack

### 🧹 Frontend

* React 18, TypeScript, Vite
* Tailwind CSS
* Zustand, React Query
* React Router DOM, Lucide Icons
* Socket.IO client, React Dropzone
* Markdown, Emoji Picker

### 🚀 Backend

* FastAPI, Uvicorn, Pydantic
* Motor (MongoDB), Redis
* WebSockets, JWT (Python-Jose)
* MinIO SDK, Passlib

### 🧱 Infrastructure

* Docker & Docker Compose
* Helm Charts for Kubernetes
* GitHub Actions CI/CD
* LiveKit Server for video
* PNPM + TurboRepo

---

## 🏗️ Architecture

### System Architecture

```mermaid
graph TB
  subgraph Client
    A[React UI] --> B[WebSocket]
  end
  subgraph Gateway
    C[FastAPI Gateway] --> D[Auth, Channels, Messages, Files]
  end
  subgraph Services
    D --> E[MongoDB]
    D --> F[Redis]
    D --> G[MinIO]
    D --> H[LiveKit]
  end
```

### Microservices View

```mermaid
graph LR
  A[Web/Mobile Client] --> B[API Gateway]
  B --> C[Auth Service]
  B --> D[Message Service]
  B --> E[File Service]
  B --> F[Video Service]
  C --> G[MongoDB]
  D --> G
  D --> H[Redis]
  E --> I[MinIO]
  F --> J[LiveKit]
```

---

## 💄️ Database Schema

### User

```mermaid
erDiagram
  USER {
    ObjectId id PK
    string email
    string username
    string hashed_password
    string avatar
    datetime created_at
  }
```

### Channel

```mermaid
erDiagram
  CHANNEL {
    ObjectId id PK
    string name
    ObjectId created_by FK
  }
```

### Message

```mermaid
erDiagram
  MESSAGE {
    ObjectId id PK
    string content
    ObjectId channel_id FK
    ObjectId user_id FK
    ObjectId thread_id FK
    array reactions
    datetime created_at
  }
```

---

## 📚 Documentation

### Project Structure

```
slack-clone/
├── apps/
│   ├── api/         # FastAPI backend
│   └── web/         # React frontend
├── docker-compose.yml
├── helm/            # Helm charts
└── livekit.yaml     # LiveKit config
```

### Concepts

* JWT-based Auth flow
* Live WebSocket chat engine
* Secure file uploads to MinIO
* Real-time user presence
* Threaded messages with Markdown

---

## 🔌 API Reference

### 🔐 Auth

* `POST /auth/register`
* `POST /auth/login`

### 📨 Channels

* `GET /channels`
* `POST /channels`

### 📩 Messages

* `GET /messages/:channel_id`
* `POST /messages`

### 📁 Files

* `POST /files/upload`

### 📹 Video

* `POST /video/token`

---

## 🚀 Quick Start

### Prerequisites

* Docker & Docker Compose
* Node 18+
* Python 3.8+
* PNPM

### Clone and Start

```bash
git clone https://github.com/yourusername/slack-clone.git
cd slack-clone
docker-compose up -d
```

### Seed Database

```bash
docker-compose exec api python scripts/seed.py
```

---

## 🐳 Docker Installation

```bash
# Build & run
docker-compose up -d

# Stop all
docker-compose down
```

---

## 🔧 Development Setup

### Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd apps/web
pnpm install
pnpm dev
```

---

## 🧪 Testing

### Backend

```bash
cd apps/api
pytest
pytest --cov=app --cov-report=html
```

### Frontend

```bash
cd apps/web
pnpm test
```

---

## 📦 Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
helm install slack-clone ./helm
helm upgrade slack-clone ./helm
```

---

## 🤝 Contributing

### How to Contribute

1. Fork this repo
2. Create a new branch
3. Commit your changes
4. Open a Pull Request

### Contribution Guidelines

* Follow existing code style
* Add relevant tests
* Use clear commit messages

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ❤️ Acknowledgements

* [LiveKit](https://livekit.io/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [MinIO](https://min.io/)
* [MongoDB](https://www.mongodb.com/)
* [React](https://react.dev/)

---

## 🧑‍💻 Made by Sanket with ❤️

> Feel free to ⭐ the repo if you like it!

* 🔗 [LinkedIn](https://linkedin.com/in/psanket18)
* 🐦 [Twitter](https://twitter.com/p_sanket18)
* 💻 [GitHub](https://github.com/sanketp1)