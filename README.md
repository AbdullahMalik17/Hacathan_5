# Customer Success Digital FTE 🤖

> **An AI-powered customer support platform that works 24/7 across Email, WhatsApp, and Web chat/form — with smart escalation to humans when needed.**

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](#tech-stack)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js-000000)](#tech-stack)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-336791)](#tech-stack)
[![Queue](https://img.shields.io/badge/Streaming-Apache%20Kafka-E10098)](#tech-stack)

---

## 🌟 What is this project?

Customer Success Digital FTE is a production-style **AI customer support system** designed to help teams scale support quality without scaling headcount at the same pace.

It combines:
- **Multi-channel intake** (Gmail, Twilio WhatsApp, Web form)
- **AI-driven resolution** (OpenAI agent + knowledge base search)
- **Operational reliability** (Kafka queueing, retries, deduplication)
- **Human-in-the-loop safety** (automatic escalation rules)
- **Modern UX** (Next.js frontend for support interactions and ticket tracking)

If your goal is to build a modern support operation that feels fast, consistent, and always-on, this project is a strong reference implementation.

---

## 🚀 Why this project can become popular

This repository is not just a demo chatbot. It models how real teams ship AI support in production:

- ✅ **Clear business value:** faster response times + reduced support load
- ✅ **Real channel integrations:** email, WhatsApp, and web intake
- ✅ **Strong architecture:** event-driven processing with Kafka
- ✅ **Enterprise-friendly foundations:** observability, readiness checks, structured logs
- ✅ **Extensible design:** documented specs, deployment guides, and modular services

---

## ✨ Core capabilities

### 1) Omnichannel customer intake
- Gmail Pub/Sub webhook handling
- Twilio WhatsApp webhook handling
- Web support form submission API

### 2) AI support agent
- Uses OpenAI-based agent logic to:
  - search knowledge base (vector search)
  - create/update ticket workflows
  - generate channel-appropriate responses
  - decide when escalation is required

### 3) Knowledge base + semantic retrieval
- PostgreSQL + `pgvector`
- Embedding-based search for relevant support articles and context

### 4) Ticketing and continuity
- Ticket creation and tracking
- Cross-channel customer identity continuity
- Conversation and message history support

### 5) Reliability and operations
- Kafka-backed async processing
- Retry and dead-letter patterns
- Correlation IDs + structured logging
- Health/readiness/metrics endpoints

### 6) Frontend experience
- Marketing/landing page
- Chat interface (`/chat`)
- Support portal (`/support`)
- Ticket lookup page (`/ticket/[id]`)

---

## 🏗️ High-level architecture

```text
Customer (Email / WhatsApp / Web)
          │
          ▼
  FastAPI Webhooks & API
          │
          ▼
      Kafka Topics
          │
          ▼
    Worker Processor
          │
          ▼
   AI Agent + Tooling
          │
    ┌─────┴───────────────┐
    ▼                     ▼
PostgreSQL/pgvector    Channel Clients
(tickets, KB, users)   (Gmail, Twilio)
```

---

## 🧰 Tech stack

- **Backend:** FastAPI, Pydantic, AsyncPG
- **AI:** OpenAI agent pattern + embeddings
- **Queue/Streaming:** Apache Kafka
- **Data:** PostgreSQL + pgvector
- **Frontend:** Next.js (App Router), React, TailwindCSS
- **Infra:** Docker Compose, Kubernetes manifests, Fly.io/Azure deployment support
- **Observability:** Prometheus + Grafana configs, JSON structured logs

---

## ⚡ Quick start (local)

### Prerequisites
- Docker Desktop (or Docker Engine)
- Python 3.10+
- Node.js 18+
- OpenAI API key

### 1) Configure backend environment

```bash
echo 'OPENAI_API_KEY=sk-proj-your-key-here' >> backend/.env
```

### 2) Start infrastructure and backend dependencies

```bash
./scripts/deploy.sh
```

### 3) Run backend API

```bash
python -m backend.src.main
```

### 4) Run background worker

```bash
python backend/src/workers/message_processor.py
```

### 5) Run frontend

```bash
cd frontend
npm install
npm run dev
```

### 6) Verify service health

```bash
./scripts/check_status.sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

---

## 🔌 Main API endpoints

- `GET /` → service metadata
- `GET /health` → liveness
- `GET /ready` → readiness (DB + Kafka)
- `GET /metrics` → Prometheus metrics
- `POST /webhooks/gmail/pubsub` → Gmail inbound notifications
- `POST /webhooks/twilio/whatsapp` → WhatsApp inbound messages
- `POST /api/support/submit` → Web form ticket creation
- `GET /api/ticket/{ticket_id}` → Ticket tracking

---

## 📁 Project structure

```text
backend/src/
├── agent/            # AI tools, prompts, response formatters
├── services/         # DB, Kafka, auth, channel clients
├── webhooks/         # Gmail, Twilio, web form handlers
├── workers/          # Kafka consumer/processor
├── monitoring/       # Metrics + monitoring config
├── middleware/       # Correlation IDs, logging, metrics
└── main.py           # FastAPI app entrypoint

frontend/
├── app/              # Next.js routes (/, /chat, /support, /ticket/[id])
└── components/       # UI and motion components

database/
├── schema.sql
└── migrations/

infrastructure/
├── docker-compose.yml
├── kubernetes/
└── monitoring/
```

---

## 🧪 Testing

```bash
# Backend test suite
python -m pytest backend/tests

# Optional helper script
./scripts/run_tests.sh
```

See `docs/TESTING.md` for detailed testing workflows.

---

## 📚 Documentation index

- `docs/API_KEYS_GUIDE.md` – how to obtain required API keys
- `docs/DEPLOY_LOCAL.md` – local Kubernetes deployment
- `docs/DEPLOY_CLOUD.md` – cloud deployment guidance
- `docs/DEPLOY_FLY.md` – Fly.io deployment path
- `docs/azure-deployment-guide.md` – Azure deployment guide
- `specs/001-customer-success-fte/` – full spec-driven implementation docs

---

## 🗺️ Roadmap ideas (to grow adoption)

To make this project even more popular, consider adding:
- Public demo environment with seeded sample tickets
- Video walkthrough + architecture diagram in docs
- Benchmarks (response time, resolution rate, cost per ticket)
- OAuth + role-based dashboard for support teams
- Native integrations (Zendesk, Intercom, HubSpot, Slack)
- Automated evaluation suite for answer quality and hallucination checks

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repo
2. Create a feature branch
3. Add/modify tests
4. Open a PR with clear context and screenshots (if UI changes)

---

## 📝 License

Copyright © 2026. All rights reserved.

---

## 💬 One-line pitch you can use publicly

**Customer Success Digital FTE is an open-source, production-style AI support platform that resolves customer issues across email, WhatsApp, and web — instantly, reliably, and with human escalation built in.**
