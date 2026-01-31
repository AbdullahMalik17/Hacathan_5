# Phase 3 Deployment Guide

## Current Status ✅

**Completed:**
- ✅ Phase 1: Project setup
- ✅ Phase 2: Foundational infrastructure (database, Kafka, models, services)
- ✅ Phase 3: Email support channel implementation (all 21 tasks)

**Ready to Deploy:**
- FastAPI application with email webhook
- OpenAI Agents SDK with 5 function tools
- Kafka consumer worker
- PostgreSQL schema with pgvector
- Knowledge base seed script
- Kafka topics setup script

---

## Prerequisites

Before running deployment scripts:

1. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for "Docker Desktop is running" status
   - Verify: `docker ps` (should not error)

2. **Set OpenAI API Key**
   ```bash
   # Edit backend/.env and add your key:
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

3. **Verify Python Environment**
   ```bash
   python --version  # Should be 3.10+
   pip list | grep -E "fastapi|pydantic|openai"  # Check dependencies
   ```

---

## Step-by-Step Deployment

### Step 1: Start Infrastructure (5 min)

```bash
# 1. Start Docker Desktop (GUI application)

# 2. Verify Docker is running
docker ps

# 3. Start PostgreSQL + Kafka
cd infrastructure
docker-compose up -d

# 4. Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Expected output:
# NAME                           STATUS
# customer-success-postgres      Up (healthy)
# customer-success-zookeeper     Up
# customer-success-kafka         Up (healthy)

# 5. Check logs if needed
docker-compose logs -f postgres  # Ctrl+C to exit
```

### Step 2: Initialize Database Schema (1 min)

```bash
# Option A: Schema auto-loaded via docker-compose volume mount
# (Already configured in docker-compose.yml)

# Option B: Manual schema load (if needed)
docker exec -i customer-success-postgres psql -U postgres -d customer_success < database/schema.sql

# Verify tables created
docker exec -it customer-success-postgres psql -U postgres -d customer_success -c "\dt"

# Expected: 7 tables
# customers, customer_identifiers, conversations, tickets,
# messages, knowledge_base, processed_messages
```

### Step 3: Seed Knowledge Base (2-3 min)

```bash
# Make script executable
chmod +x scripts/seed_knowledge_base.py

# IMPORTANT: Ensure OPENAI_API_KEY is set in backend/.env
# Edit backend/.env and add:
# OPENAI_API_KEY=sk-proj-your-actual-key-here

# Run seeding script
python scripts/seed_knowledge_base.py

# Expected output:
# Connected to database
# Processing article 1/10: How to Reset Your Password
# ✓ Seeded: How to Reset Your Password
# ...
# Processing article 10/10: Payment Methods and Billing
# ✓ Seeded: Payment Methods and Billing
# Knowledge base seeding complete!
# Total articles in knowledge base: 10

# Verify seeding
docker exec -it customer-success-postgres psql -U postgres -d customer_success \
  -c "SELECT COUNT(*), AVG(array_length(embedding, 1)) FROM knowledge_base;"

# Expected: count = 10, avg embedding dimension = 1536
```

### Step 4: Setup Kafka Topics (1 min)

```bash
# Make script executable
chmod +x scripts/setup_kafka_topics.sh

# Run Kafka setup
bash scripts/setup_kafka_topics.sh

# Expected output:
# Creating topic: fte.tickets.incoming
#   ✓ Topic created successfully
# Creating topic: fte.channels.email.inbound
#   ✓ Topic created successfully
# ...
# Creating topic: fte.dlq
#   ✓ Topic created successfully
#
# Kafka topics setup complete!

# Verify topics
docker exec customer-success-kafka kafka-topics.sh \
  --list --bootstrap-server localhost:9092 | grep fte

# Expected: 10 topics starting with "fte."
```

### Step 5: Start Application Services (2 min)

```bash
# Terminal 1: Start FastAPI server
python -m backend.src.main

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# Structured logging initialized at INFO level
# Database pool initialized: min=10, max=20
# Kafka producer initialized
# Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000

# Test health endpoint (in another terminal):
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"customer-success-fte"}

curl http://localhost:8000/ready
# Expected: {"status":"ready","database":"connected","kafka":"connected"}
```

```bash
# Terminal 2: Start Kafka Consumer Worker
python backend/src/workers/message_processor.py

# Expected output:
# Starting message processor worker...
# Connected to database
# Database pool initialized: min=10, max=20
# Kafka producer initialized
# Kafka consumer created: group=agent-workers
# Message processor started. Listening for messages...
```

---

## Testing the Deployment

### Quick Test: Publish Test Message

```bash
# In Python REPL or script:
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, 'backend/src')

from services.kafka_producer import kafka_producer
from services.database import db_service
from uuid import uuid4
from datetime import datetime

async def test():
    await db_service.connect()
    kafka_producer.connect()

    test_message = {
        "channel": "email",
        "customer_identifier": "test@example.com",
        "content": "How do I reset my password? I forgot my login credentials.",
        "channel_message_id": f"test-{uuid4()}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "subject": "Password Reset Help",
            "thread_id": "thread_test123"
        }
    }

    correlation_id = await kafka_producer.publish(
        topic="fte.tickets.incoming",
        message=test_message,
        key="test@example.com"
    )

    print(f"✓ Test message published: {correlation_id}")
    print("Check Kafka consumer logs for processing...")

    kafka_producer.disconnect()
    await db_service.disconnect()

asyncio.run(test())
EOF
```

**Expected Consumer Logs:**
```
INFO: Invoking agent: customer=<uuid>, channel=email
INFO: Agent processing complete
INFO: Email sent: to=test@example.com
INFO: Message processed successfully
```

**Verify in Database:**
```bash
docker exec -it customer-success-postgres psql -U postgres -d customer_success \
  -c "SELECT email FROM customers WHERE email LIKE 'test%';"

docker exec -it customer-success-postgres psql -U postgres -d customer_success \
  -c "SELECT id, source_channel, status, category FROM tickets LIMIT 3;"
```

---

## Monitoring & Debugging

### Check Kafka Topics

```bash
# List all topics
docker exec customer-success-kafka kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# Describe a topic
docker exec customer-success-kafka kafka-topics.sh \
  --describe --topic fte.tickets.incoming \
  --bootstrap-server localhost:9092

# Check consumer group lag
docker exec customer-success-kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group agent-workers
```

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it customer-success-postgres psql -U postgres -d customer_success

# Useful queries:
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM tickets;
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM knowledge_base;

# Check recent tickets
SELECT id, source_channel, status, created_at
FROM tickets
ORDER BY created_at DESC
LIMIT 5;
```

### Check Logs

```bash
# Docker Compose logs
cd infrastructure
docker-compose logs -f  # All services
docker-compose logs -f postgres  # Just PostgreSQL
docker-compose logs -f kafka  # Just Kafka

# Application logs (stdout)
# Already shown in terminals running FastAPI and worker
```

---

## Troubleshooting

### Issue: Docker Compose fails to start

**Solution:**
1. Ensure Docker Desktop is running
2. Check Docker resources (Settings > Resources):
   - Memory: At least 4GB
   - CPUs: At least 2
3. Try: `docker-compose down` then `docker-compose up -d`

### Issue: Knowledge base seeding fails with "OPENAI_API_KEY not set"

**Solution:**
```bash
# Edit backend/.env
nano backend/.env  # or use your editor

# Add your actual API key:
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Save and re-run
python scripts/seed_knowledge_base.py
```

### Issue: Kafka topics script fails

**Solution:**
```bash
# Verify Kafka is healthy
docker exec customer-success-kafka kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092

# If timeout, wait 30 seconds for Kafka to fully start
sleep 30

# Re-run script
bash scripts/setup_kafka_topics.sh
```

### Issue: Consumer not processing messages

**Solution:**
1. Check Kafka connection:
   ```bash
   docker exec customer-success-kafka kafka-console-consumer.sh \
     --bootstrap-server localhost:9092 \
     --topic fte.tickets.incoming --from-beginning
   ```
2. Check consumer group:
   ```bash
   docker exec customer-success-kafka kafka-consumer-groups.sh \
     --bootstrap-server localhost:9092 --list
   ```
3. Restart worker: Ctrl+C and re-run `python backend/src/workers/message_processor.py`

---

## Success Criteria ✅

Deployment is successful when:

- [  ] Docker services are running (postgres, zookeeper, kafka)
- [  ] Database schema created (7 tables)
- [  ] Knowledge base seeded (10 articles with embeddings)
- [  ] Kafka topics created (10 topics)
- [  ] FastAPI server healthy (`/health` returns 200)
- [  ] FastAPI ready (`/ready` shows database+kafka connected)
- [  ] Kafka consumer listening for messages
- [  ] Test message published and processed
- [  ] Customer and ticket created in database

---

## Next Steps After Deployment

1. **Configure Gmail Pub/Sub** (for production):
   - Follow `infrastructure/kubernetes/configmaps/gmail-config.yaml`
   - Set up Google Cloud project
   - Enable Gmail API
   - Create Pub/Sub topic and subscription
   - Configure webhook endpoint

2. **Test Email Flow** (end-to-end):
   - Send email to support@company.com
   - Verify Pub/Sub notification received
   - Check agent processing in logs
   - Verify email response sent

3. **Deploy Phase 4** (WhatsApp support):
   - Proceed with User Story 2 implementation

4. **Production Deployment**:
   - Deploy to Kubernetes using manifests in `infrastructure/kubernetes/`
   - Configure environment-specific secrets
   - Set up monitoring and alerting

---

## Quick Start Command (All-in-One)

```bash
#!/bin/bash
set -e

echo "🚀 Starting Customer Success Digital FTE Deployment"

# 1. Start Docker services
cd infrastructure
docker-compose up -d
echo "✓ Docker services started"
sleep 30  # Wait for Kafka

cd ..

# 2. Seed knowledge base
echo "Seeding knowledge base..."
python scripts/seed_knowledge_base.py
echo "✓ Knowledge base seeded"

# 3. Setup Kafka topics
echo "Setting up Kafka topics..."
bash scripts/setup_kafka_topics.sh
echo "✓ Kafka topics created"

# 4. Instructions for starting services
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Terminal 1: python -m backend.src.main"
echo "2. Terminal 2: python backend/src/workers/message_processor.py"
echo "3. Test: curl http://localhost:8000/health"
```

Save as `deploy.sh`, make executable with `chmod +x deploy.sh`, and run with `./deploy.sh`
