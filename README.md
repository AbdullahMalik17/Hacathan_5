# Customer Success Digital FTE 🤖

> **An AI-native customer support platform that resolves conversations across Email, WhatsApp, Web Form, and Chat—with smart escalation to humans when needed.**

Customer Success Digital FTE is a full-stack project built for modern support teams that want to deliver **fast, accurate, and always-on customer help** without sacrificing quality.

---

## Why this project matters

Most support teams struggle with the same problems:

- Long response times during peak hours
- Fragmented customer context across channels
- Repetitive tickets that drain human agents
- Limited 24/7 coverage

This project solves those challenges by combining:

- **AI-driven response generation**
- **Cross-channel identity + conversation tracking**
- **Knowledge base semantic search with vector embeddings**
- **Automated ticketing and escalation workflows**

The result: a practical "Digital FTE" (full-time equivalent) that can absorb a large portion of support workload while keeping complex issues routed to real people.

---

## What you can do with Customer Success Digital FTE

### ✅ Multi-channel support intake
- Gmail Pub/Sub webhook for email tickets
- Twilio webhook for WhatsApp messages
- Web support form for direct submissions
- Chat experience from the frontend

### ✅ AI-powered ticket handling
- Context-aware support responses
- Sentiment-aware prompt logic
- Tool-enabled agent actions (ticketing, history lookup, KB search, escalation)
- Channel-specific response formatting

### ✅ Reliable backend processing
- Kafka-backed async processing pipeline
- Retry logic + dead letter handling patterns
- Message deduplication support
- Structured logging + correlation IDs for tracing

### ✅ Knowledge retrieval and memory
- PostgreSQL + pgvector semantic search
- OpenAI embeddings-based retrieval
- Customer and conversation history for continuity

### ✅ Support operations readiness
- Health/readiness endpoints
- Prometheus metrics endpoint
- Deployment scripts and runbooks
- Dockerized local environment

---

## High-level architecture

```text
Customer (Email / WhatsApp / Web / Chat)
        |
        v
Webhook/API Layer (FastAPI)
        |
        v
Kafka Topics (event queue)
        |
        v
Worker Processor
        |
        v
AI Agent + Tools + Knowledge Base Search
        |
        +--> PostgreSQL (tickets, conversations, history, KB)
        |
        +--> Channel adapters (Email / WhatsApp / Web response flow)
```

---

## Tech stack

### Backend
- **FastAPI** for API + webhooks
- **Python 3.10+**
- **Kafka** for async message processing
- **PostgreSQL + pgvector** for relational + semantic search
- **OpenAI APIs** for response generation and embeddings

### Frontend
- **Next.js** (App Router)
- **React + TypeScript**
- **Tailwind CSS + Radix UI**

### Infrastructure
- **Docker / Docker Compose**
- Deploy helpers for cloud platforms (see `docs/`)

---

## Project structure

```text
.
├── backend/                 # FastAPI app, agent logic, workers, tests
├── frontend/                # Next.js UI (landing, chat, support pages)
├── database/                # SQL schema
├── infrastructure/          # Docker Compose and infra configs
├── scripts/                 # Deployment, health checks, seed scripts
├── docs/                    # Deployment + testing documentation
└── README.md
```

---

## Quick start (local)

### 1) Prerequisites
- Docker Desktop
- Python 3.10+
- Node.js 18+
- OpenAI API key

### 2) Configure environment

```bash
cp backend/.env.example backend/.env
# then set OPENAI_API_KEY in backend/.env
```

### 3) Start core infrastructure

```bash
./scripts/deploy.sh
```

### 4) Run backend app + worker

```bash
python -m backend.src.main
python backend/src/workers/message_processor.py
```

### 5) Run frontend (optional but recommended)

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`
Backend API: `http://localhost:8000`

---

## Key API endpoints

### Platform health
- `GET /` - service metadata
- `GET /health` - liveness probe
- `GET /ready` - readiness probe (DB + Kafka)
- `GET /metrics` - Prometheus metrics

### Channel webhooks and support APIs
- `POST /webhooks/gmail/pubsub`
- `POST /webhooks/twilio/whatsapp`
- `POST /api/support/submit`
- `GET /api/ticket/{ticket_id}`

---

## Documentation

- `docs/API_KEYS_GUIDE.md` - getting all required keys
- `docs/DEPLOY_LOCAL.md` - local deployment options
- `docs/DEPLOY_CLOUD.md` - cloud deployment guidance
- `docs/TESTING.md` - test scenarios and validation
- `docs/DEPLOYMENT_GUIDE.md` - detailed deployment reference

---

## Who this project is for

This project is great for:

- Hackathon demos and AI product showcases
- Startups building support automation MVPs
- Teams experimenting with AI + human hybrid support
- Developers learning event-driven AI architecture

---

## How to make this project popular 🚀

If you want this project to gain visibility quickly:

1. **Add a short demo video/GIF** to this README (home page + ticket flow).
2. **Publish sample prompts and test conversations** in `docs/`.
3. **Share architecture screenshots** (system flow + database model).
4. **Write a "How it works" post** on LinkedIn/Medium and link this repo.
5. **Add badges** (build status, license, tech stack, stars).
6. **Open "good first issue" tasks** to attract contributors.
7. **Deploy a live demo** and include the URL in this README.

---

## Roadmap ideas

- Agent analytics dashboard (resolution quality, escalation rate)
- Multilingual support
- CRM integrations (HubSpot, Salesforce, Zendesk)
- Fine-grained role-based admin panel
- Auto-summarized handoff notes for human agents

---

## Contributing

Contributions are welcome. A good starting point:

1. Check existing docs and scripts.
2. Run local environment successfully.
3. Propose focused improvements (UX, reliability, observability, integration).
4. Submit a clean PR with tests and notes.

---

## License

No explicit OSS license is currently defined in this repository. Add a `LICENSE` file (for example MIT/Apache-2.0) if you want open-source adoption and easier external contributions.

---

## Final one-line pitch

**Customer Success Digital FTE is a production-minded AI customer support engine that combines multi-channel intake, intelligent automation, and human escalation into one scalable platform.**
