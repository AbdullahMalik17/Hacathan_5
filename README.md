# Customer Success Digital FTE 🤖

AI-powered customer support agent that handles inquiries 24/7 across Email, WhatsApp, and Web Form channels.

## Project Status

### ✅ Completed Phases

| Phase | Description | Status | Tasks |
|-------|-------------|--------|-------|
| **Phase 1** | Project Setup | ✅ Complete | 9/9 |
| **Phase 2** | Foundational Infrastructure | ✅ Complete | 13/13 |
| **Phase 3** | Email Support (P1 MVP) | ✅ Complete | 21/21 |
| **Phase 4** | WhatsApp Support (P1 MVP) | ⏳ Pending | 0/14 |
| **Phase 5** | Web Form Support (P2) | ⏳ Pending | 0/15 |

**Total Progress: 43/117 tasks (37%)**

---

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** - Running and healthy
2. **Python 3.10+** - With virtual environment
3. **OpenAI API Key** - For agent and embeddings

### One-Command Deployment

```bash
# 1. Start Docker Desktop (GUI)

# 2. Set your OpenAI API key
echo 'OPENAI_API_KEY=sk-proj-your-key-here' >> backend/.env

# 3. Run deployment script
./deploy.sh

# 4. Start services (in separate terminals)
python -m backend.src.main                    # FastAPI server
python backend/src/workers/message_processor.py  # Kafka consumer

# 5. Check status
./check_status.sh
```

---

## 📁 Project Structure

```
customer-success-fte/
├── backend/src/
│   ├── agent/                 # AI Agent (OpenAI Agents SDK)
│   │   ├── customer_success_agent.py  # Main agent
│   │   ├── tools.py           # 5 function tools
│   │   ├── prompts.py         # System prompts
│   │   └── formatters.py      # Channel-specific formatting
│   ├── webhooks/              # Webhook handlers
│   │   └── gmail.py           # Gmail Pub/Sub handler
│   ├── services/
│   │   ├── database.py        # AsyncPG connection pool
│   │   ├── kafka_producer.py  # Kafka producer
│   │   ├── auth.py            # Webhook validation
│   │   └── channels/
│   │       └── gmail_client.py  # Gmail API client
│   ├── workers/
│   │   └── message_processor.py  # Kafka consumer
│   ├── models/                # Pydantic models
│   ├── middleware/            # Correlation ID, logging
│   ├── utils/                 # Sanitization utilities
│   ├── config.py              # Configuration management
│   └── main.py                # FastAPI application
├── database/
│   ├── schema.sql             # PostgreSQL schema + pgvector
│   └── migrations/
├── infrastructure/
│   ├── docker-compose.yml     # Local dev environment
│   └── kubernetes/            # K8s manifests (Phase 8)
├── scripts/
│   ├── seed_knowledge_base.py  # Seed KB with embeddings
│   └── setup_kafka_topics.sh   # Create Kafka topics
├── deploy.sh                  # Deployment script
├── check_status.sh            # Status checker
├── DEPLOYMENT_GUIDE.md        # Full deployment guide
└── TESTING.md                 # Testing guide
```

---

## 🎯 Features Implemented

### Phase 3: Email Support Channel

- ✅ **Gmail Integration**
  - Pub/Sub webhook with JWT validation
  - Gmail API for sending formatted responses
  - Email threading for conversation continuity

- ✅ **AI Agent (OpenAI Agents SDK)**
  - Autonomous customer support agent
  - 5 function tools: `create_ticket`, `get_customer_history`, `search_knowledge_base`, `send_email_response`, `escalate_ticket`
  - Comprehensive system prompts with sentiment analysis
  - Escalation detection (pricing, refund, legal, sentiment, human request)

- ✅ **Knowledge Base Search**
  - Semantic search with pgvector (1536-dim embeddings)
  - OpenAI text-embedding-3-small model
  - Similarity threshold: 0.6
  - HNSW index for fast retrieval

- ✅ **Message Processing**
  - Kafka consumer with exponential backoff retry
  - Message deduplication (FR-004)
  - Cross-channel customer identity
  - Graceful error handling + DLQ

- ✅ **Database Layer**
  - PostgreSQL with pgvector extension
  - 7 entities: customers, customer_identifiers, conversations, tickets, messages, knowledge_base, processed_messages
  - AsyncPG connection pool (min=10, max=20)

- ✅ **Middleware & Security**
  - Correlation ID tracking (distributed tracing)
  - Structured JSON logging
  - Input sanitization (XSS, SQL injection prevention)
  - Webhook signature validation

---

## 🔧 Architecture

```
┌──────────────┐
│   Customer   │
│  sends email │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│  Gmail + Pub/Sub    │  ← Webhook notification
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  FastAPI Webhook    │  ← JWT validation
│  /webhooks/gmail    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Kafka Topic       │  ← fte.tickets.incoming
│  (Message Queue)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Kafka Consumer     │  ← Retry logic + DLQ
│  (Worker Process)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   AI Agent          │  ← OpenAI Agents SDK
│  - Search KB        │
│  - Create ticket    │
│  - Analyze sentiment│
│  - Generate response│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Gmail API          │  ← Send formatted email
│  (Send Response)    │
└─────────────────────┘
          │
          ▼
     Customer receives
     professional response
```

---

## 🧪 Testing

### Manual Testing

1. **Check Infrastructure**
   ```bash
   ./check_status.sh
   ```

2. **Test Health Endpoints**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/ready
   ```

3. **Publish Test Message**
   ```bash
   # See TESTING.md for full test script
   python -c "
   import asyncio
   from backend.src.services.kafka_producer import kafka_producer
   asyncio.run(kafka_producer.publish('fte.tickets.incoming', {
       'channel': 'email',
       'customer_identifier': 'test@example.com',
       'content': 'How do I reset my password?',
       'channel_message_id': 'test-123',
       'timestamp': '2026-01-31T12:00:00Z',
       'metadata': {'subject': 'Help'}
   }))
   "
   ```

4. **Verify Processing**
   ```bash
   # Check database
   docker exec -it customer-success-postgres psql -U postgres -d customer_success \
     -c "SELECT COUNT(*) FROM tickets;"
   ```

### End-to-End Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

---

## 📊 Database Schema

```sql
customers (id, name, email, phone, sentiment_score, ...)
├── customer_identifiers (email, phone, whatsapp)
└── conversations (active/closed)
    ├── tickets (open/in_progress/resolved/escalated)
    └── messages (inbound/outbound)

knowledge_base (id, title, content, embedding[1536], ...)
```

---

## 🔑 Environment Variables

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_success

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=agent-workers

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here  # ⚠️ REQUIRED
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Gmail (for production)
GMAIL_SERVICE_ACCOUNT_PATH=./credentials/gmail-service-account.json
GMAIL_SUPPORT_EMAIL=support@company.com

# Twilio (Phase 4)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment instructions
- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [CLAUDE.md](CLAUDE.md) - Project development guidelines
- [specs/001-customer-success-fte/](specs/001-customer-success-fte/) - Feature specifications

---

## 🎯 Next Steps

### Option 1: Complete MVP (Recommended)
Proceed with **Phase 4: WhatsApp Support** to complete the dual-channel P1 MVP.

### Option 2: Production Deployment
1. Set up Gmail Pub/Sub (see `infrastructure/kubernetes/configmaps/gmail-config.yaml`)
2. Configure Kubernetes secrets
3. Deploy to production cluster
4. Set up monitoring and alerts

### Option 3: Expand Features
- Phase 5: Web Form Support
- Phase 6: Cross-Channel Continuity
- Phase 7: Advanced Escalation Logic

---

## 🤝 Contributing

This project follows Spec-Driven Development (SDD) methodology:
1. All features start with specifications in `specs/`
2. Tasks are tracked in `specs/*/tasks.md`
3. ADRs document architectural decisions in `history/adr/`
4. PHRs record development history in `history/prompts/`

---

## 📝 License

Copyright © 2026. All rights reserved.

---

## 🆘 Support

- **Issues**: Check DEPLOYMENT_GUIDE.md troubleshooting section
- **Status**: Run `./check_status.sh`
- **Logs**: `docker-compose -f infrastructure/docker-compose.yml logs -f`

---

**Built with:**
- FastAPI
- OpenAI Agents SDK
- PostgreSQL + pgvector
- Apache Kafka
- Docker

**AI Agent powered by**: OpenAI GPT-4 Turbo
