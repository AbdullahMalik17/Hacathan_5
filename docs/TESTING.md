# Phase 3 Testing Guide: Email Support Channel

## Prerequisites Checklist

Before testing, ensure you have:

- [ ] PostgreSQL running locally or accessible
- [ ] Kafka & Zookeeper running (via Docker Compose)
- [ ] Python virtual environment activated
- [ ] All dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] Environment variables configured (`.env` file)
- [ ] OpenAI API key set in environment
- [ ] Gmail service account credentials (optional for full test)

## Quick Environment Check

```bash
# 1. Check Python environment
python --version  # Should be 3.10+

# 2. Check PostgreSQL
psql -U postgres -c "SELECT version();"

# 3. Check Kafka (via Docker)
docker ps | grep kafka

# 4. Check environment variables
cat backend/.env.example
```

## Step-by-Step Testing

### Test 1: Database Schema ✅

```bash
# Create database
psql -U postgres -c "CREATE DATABASE customer_success;"

# Run schema
psql -U postgres -d customer_success -f database/schema.sql

# Verify tables
psql -U postgres -d customer_success -c "\dt"
```

**Expected Output:** 7 tables (customers, customer_identifiers, conversations, tickets, messages, knowledge_base, processed_messages)

### Test 2: Seed Knowledge Base ✅

```bash
# Make script executable
chmod +x scripts/seed_knowledge_base.py

# Run seeding
python scripts/seed_knowledge_base.py
```

**Expected Output:** 10 articles seeded with embeddings

### Test 3: Setup Kafka Topics ✅

```bash
# Start Kafka (if not running)
docker-compose -f infrastructure/docker-compose.yml up -d

# Make script executable
chmod +x scripts/setup_kafka_topics.sh

# Create topics
bash scripts/setup_kafka_topics.sh
```

**Expected Output:** Topics created: fte.tickets.incoming, fte.channels.*, fte.escalations, fte.dlq

### Test 4: Start FastAPI Server

```bash
# From project root
python -m backend.src.main
```

**Expected Output:**
- Server starts on http://localhost:8000
- Health check: http://localhost:8000/health returns `{"status":"healthy"}`
- Readiness: http://localhost:8000/ready shows database and Kafka connected

### Test 5: Start Kafka Consumer Worker

```bash
# In a separate terminal
python backend/src/workers/message_processor.py
```

**Expected Output:** "Message processor started. Listening for messages..."

### Test 6: Test Agent Tools (Python REPL)

```python
import asyncio
import sys
sys.path.insert(0, 'backend/src')

from agent.tools import search_knowledge_base
from services.database import db_service
from config import get_settings

async def test():
    settings = get_settings()
    await db_service.connect()

    # Test knowledge base search
    result = await search_knowledge_base("password reset", max_results=3)
    print(f"Found {result['count']} articles")
    print(f"Top result: {result['results'][0]['title']}")

    await db_service.disconnect()

asyncio.run(test())
```

**Expected Output:** Articles found about password reset with similarity scores

### Test 7: Simulate Email Flow

```python
import asyncio
import sys
sys.path.insert(0, 'backend/src')

from services.kafka_producer import kafka_producer
from services.database import db_service
from uuid import uuid4

async def test():
    await db_service.connect()
    kafka_producer.connect()

    # Publish test message
    test_message = {
        "channel": "email",
        "customer_identifier": "test@example.com",
        "content": "How do I reset my password?",
        "channel_message_id": f"test-{uuid4()}",
        "timestamp": "2026-01-31T12:00:00Z",
        "metadata": {"subject": "Password Help"}
    }

    correlation_id = await kafka_producer.publish(
        topic="fte.tickets.incoming",
        message=test_message,
        key="test@example.com"
    )

    print(f"Message published: {correlation_id}")
    print("Check Kafka consumer logs for processing...")

    kafka_producer.disconnect()
    await db_service.disconnect()

asyncio.run(test())
```

**Expected Output:** Message published to Kafka, consumer processes it

### Test 8: Check Database After Processing

```bash
# Check if customer was created
psql -U postgres -d customer_success -c "SELECT * FROM customers LIMIT 5;"

# Check if ticket was created
psql -U postgres -d customer_success -c "SELECT id, source_channel, status FROM tickets LIMIT 5;"

# Check messages
psql -U postgres -d customer_success -c "SELECT channel, direction, content FROM messages LIMIT 5;"
```

### Test 9: Gmail Webhook (Manual - Requires Gmail Setup)

1. Set up Gmail Pub/Sub following `infrastructure/kubernetes/configmaps/gmail-config.yaml`
2. Send email to support@company.com
3. Check webhook logs: Should receive Pub/Sub notification
4. Check Kafka consumer logs: Should process email
5. Check customer's inbox: Should receive formatted response

## Common Issues & Solutions

### Issue: Database connection failed
**Solution:** Check DATABASE_URL in .env, ensure PostgreSQL is running

### Issue: Kafka connection failed
**Solution:**
```bash
docker-compose -f infrastructure/docker-compose.yml up -d
docker ps | grep kafka  # Verify running
```

### Issue: OpenAI API error
**Solution:** Check OPENAI_API_KEY in environment variables

### Issue: Knowledge base search returns no results
**Solution:** Run seed script again, verify embeddings were created

### Issue: Kafka consumer not processing
**Solution:**
- Check topic exists: `kafka-topics.sh --list --bootstrap-server localhost:9092`
- Check consumer group: `kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list`

## Success Criteria

✅ Database schema created with all 7 tables
✅ Knowledge base seeded with 10 articles
✅ Kafka topics created (9 topics)
✅ FastAPI server healthy and ready
✅ Kafka consumer running and listening
✅ Test message published and processed
✅ Customer, ticket, and messages created in database
✅ (Optional) Gmail webhook receives and processes email

## Next Steps After Testing

1. **Deploy to Kubernetes**: Use manifests in `infrastructure/kubernetes/`
2. **Set up Gmail Pub/Sub**: Follow gmail-config.yaml instructions
3. **Monitor**: Check logs, metrics, Kafka lag
4. **Scale**: Adjust Kafka partitions and consumer replicas as needed

---

## Quick Test Command

Run this all-in-one test:

```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# 1. Setup database
psql -U postgres -c "CREATE DATABASE customer_success;" || echo "DB exists"
psql -U postgres -d customer_success -f database/schema.sql

# 2. Seed knowledge base (requires OPENAI_API_KEY)
python scripts/seed_knowledge_base.py

# 3. Setup Kafka topics (requires Kafka running)
bash scripts/setup_kafka_topics.sh

# 4. Start services
echo "Start FastAPI: python -m backend.src.main"
echo "Start Consumer: python backend/src/workers/message_processor.py"
```
