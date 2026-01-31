# Quickstart Guide: Customer Success Digital FTE

**Feature**: 001-customer-success-fte
**Last Updated**: 2026-01-31

## Prerequisites

- **Python**: 3.11+
- **Docker**: 24.0+ with Docker Compose
- **Node.js**: 20+ (for web form frontend)
- **Kubernetes**: Minikube or cloud cluster (for deployment)
- **API Keys**:
  - OpenAI API key
  - Twilio Account SID + Auth Token
  - Gmail API service account credentials

## Local Development Setup

### 1. Clone and Setup Environment

```bash
cd E:\WEB DEVELOPMENT\Hacathan_5
git checkout 001-customer-success-fte

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables

Create `backend/.env`:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_success

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Gmail
GMAIL_SERVICE_ACCOUNT_PATH=./credentials/gmail-service-account.json

# Application
LOG_LEVEL=INFO
AGENT_RESPONSE_TIMEOUT=180
```

### 3. Start Infrastructure (Docker Compose)

```bash
# Start PostgreSQL + Kafka + Zookeeper
docker-compose up -d postgres kafka zookeeper

# Wait for services to be ready
docker-compose ps

# Initialize PostgreSQL schema
psql -h localhost -U postgres -d customer_success -f database/schema.sql

# Seed knowledge base
python scripts/seed_knowledge_base.py
```

### 4. Run Backend API

```bash
cd backend

# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verify health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 5. Run Agent Workers

```bash
# In separate terminal
cd backend
python src/workers/message_processor.py

# Worker will consume from Kafka topic: fte.tickets.incoming
```

### 6. Run Web Form Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Access at http://localhost:3000
```

## Testing

### Test Email Channel (Gmail)

```bash
# Send test email to configured Gmail address
# Subject: Password reset help
# Body: How do I reset my password?

# Check logs for processing
tail -f backend/logs/agent.log
```

### Test WhatsApp Channel

```bash
# Use Twilio Console WhatsApp Sandbox
# Send message to your Twilio number
# Example: "What are your business hours?"

# Or use curl to simulate webhook:
curl -X POST http://localhost:8000/webhooks/twilio/whatsapp \
  -H "X-Twilio-Signature: $(python scripts/generate_twilio_signature.py)" \
  -d "From=whatsapp:+14155551234&To=whatsapp:+14155238886&Body=Test+message&MessageSid=SMxxxx"
```

### Test Web Form

```bash
# Open browser to http://localhost:3000
# Fill out support form
# Submit and verify ticket ID displayed

# Check agent processing:
curl http://localhost:8000/api/ticket/{ticket_id}
```

## Project Structure

```
E:\WEB DEVELOPMENT\Hacathan_5/
├── backend/
│   ├── src/
│   │   ├── main.py                 # FastAPI app
│   │   ├── webhooks/
│   │   │   ├── gmail.py
│   │   │   ├── twilio.py
│   │   │   └── webform.py
│   │   ├── agent/
│   │   │   ├── customer_success_agent.py  # OpenAI Agents SDK
│   │   │   └── tools.py                   # @function_tool definitions
│   │   ├── workers/
│   │   │   └── message_processor.py       # Kafka consumer
│   │   ├── services/
│   │   │   ├── database.py         # asyncpg pool
│   │   │   ├── kafka_producer.py
│   │   │   └── auth.py             # Signature validation
│   │   └── middleware/
│   │       ├── correlation_id.py
│   │       └── logging.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── SupportForm.tsx
│   │   └── pages/
│   │       └── support.tsx
│   ├── package.json
│   └── next.config.js
├── database/
│   ├── schema.sql               # PostgreSQL schema
│   └── migrations/
├── infrastructure/
│   ├── kubernetes/
│   │   ├── deployments/
│   │   │   ├── api.yaml
│   │   │   ├── agent-workers.yaml
│   │   │   └── postgresql.yaml
│   │   ├── services/
│   │   └── configmaps/
│   └── docker-compose.yml
├── scripts/
│   ├── seed_knowledge_base.py
│   └── generate_twilio_signature.py
└── specs/
    └── 001-customer-success-fte/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        └── contracts/
```

## Common Issues

### PostgreSQL Connection Fails
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart if needed
docker-compose restart postgres

# Verify connection
psql -h localhost -U postgres -d customer_success -c "SELECT 1"
```

### Kafka Consumer Not Receiving Messages
```bash
# Check Kafka topics exist
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Create topic if missing
docker exec -it kafka kafka-topics --create \
  --topic fte.tickets.incoming \
  --bootstrap-server localhost:9092 \
  --partitions 12 \
  --replication-factor 1

# Test producer/consumer
python scripts/test_kafka.py
```

### OpenAI API Rate Limit
```python
# Reduce request rate in agent worker
# File: backend/src/workers/message_processor.py
# Add delay between messages:
await asyncio.sleep(1)  # 1 request per second
```

## Next Steps

1. **Run Tests**: `pytest backend/tests/`
2. **Deploy to Kubernetes**: See `infrastructure/kubernetes/README.md`
3. **Monitor Metrics**: Access Prometheus at `http://localhost:9090`
4. **View Logs**: `docker-compose logs -f api worker`

## Support

- **Issues**: GitHub Issues
- **Documentation**: `specs/001-customer-success-fte/`
- **Constitution**: `.specify/memory/constitution.md`
