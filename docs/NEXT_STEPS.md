# 🎯 Next Steps: Complete Phase 3 Deployment & Testing

## Current Status

✅ **Phase 3 Code Implementation: COMPLETE** (21/21 tasks)
- All email support channel code written
- All agent tools implemented
- All infrastructure configured

⏳ **Phase 3 Deployment: READY TO RUN**
- Scripts created and ready
- Documentation complete
- Waiting for Docker Desktop + OpenAI API key

---

## Action Plan

### Step 1: Start Docker Desktop (2 minutes)

**What to do:**
1. Open Docker Desktop application on your Windows machine
2. Wait for "Docker Desktop is running" status (green icon in system tray)
3. Verify: Open terminal and run `docker ps` (should not give error)

**Why needed:** PostgreSQL and Kafka will run in Docker containers

---

### Step 2: Set OpenAI API Key (1 minute)

**What to do:**
1. Get your OpenAI API key from https://platform.openai.com/api-keys
2. Open `backend/.env` in your editor
3. Replace the placeholder:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
4. Save the file

**Why needed:** Agent needs OpenAI for:
- Generating embeddings for knowledge base search
- Running the GPT-4 agent to answer customer questions

---

### Step 3: Run Deployment Script (5 minutes)

**What to do:**
```bash
# Run the automated deployment
./scripts/deploy.sh
```

**What it does:**
1. ✅ Starts PostgreSQL + Kafka in Docker (30 sec)
2. ✅ Creates database schema (7 tables)
3. ✅ Seeds knowledge base with 10 articles (2-3 min)
4. ✅ Creates Kafka topics (10 topics)

**Expected output:**
```
✓ Docker is running
✓ PostgreSQL is running
✓ Kafka is running
✓ Database schema loaded (7 tables)
✓ Knowledge base seeded
✓ Kafka topics created

Deployment complete!
```

---

### Step 4: Start Application Services (1 minute)

**Open TWO terminals:**

**Terminal 1 - FastAPI Server:**
```bash
python -m backend.src.main
```

Expected output:
```
INFO: Started server process
Structured logging initialized at INFO level
Database pool initialized: min=10, max=20
Kafka producer initialized
Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Kafka Consumer:**
```bash
python backend/src/workers/message_processor.py
```

Expected output:
```
Starting message processor worker...
Connected to database
Kafka consumer created: group=agent-workers
Message processor started. Listening for messages...
```

**✅ Keep both terminals running!**

---

### Step 5: Verify Deployment (2 minutes)

**Option A: Use status script**
```bash
# In a third terminal
./scripts/check_status.sh
```

Expected output:
```
✓ Docker is running
✓ PostgreSQL is healthy
  Tables: 7/7
  Knowledge base: 10 articles
  Customers: 0
  Tickets: 0
✓ Kafka is running
  Topics: 10
✓ FastAPI server is running (port 8000)
✓ FastAPI is ready (DB + Kafka connected)
✓ Kafka consumer worker is running
```

**Option B: Manual verification**
```bash
# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"customer-success-fte"}

# Test readiness
curl http://localhost:8000/ready
# Expected: {"status":"ready","database":"connected","kafka":"connected"}
```

---

### Step 6: Test Email Flow (5 minutes)

**Create test message script:**

Create file `test_email.py`:
```python
import asyncio
import sys
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, 'backend/src')

from services.kafka_producer import kafka_producer
from services.database import db_service

async def main():
    await db_service.connect()
    kafka_producer.connect()

    # Simulate email from customer
    test_message = {
        "channel": "email",
        "customer_identifier": "johndoe@example.com",
        "content": "How do I reset my password? I forgot my login credentials.",
        "channel_message_id": f"gmail-{uuid4()}",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "subject": "Password Reset Help",
            "thread_id": "thread_test123"
        }
    }

    print("📧 Publishing test email message...")
    correlation_id = await kafka_producer.publish(
        topic="fte.tickets.incoming",
        message=test_message,
        key="johndoe@example.com"
    )

    print(f"✅ Message published: {correlation_id}")
    print("\n👀 Watch Terminal 2 (Kafka Consumer) for processing...")
    print("Expected:")
    print("  1. Customer lookup/creation")
    print("  2. Conversation + ticket creation")
    print("  3. Knowledge base search for 'password reset'")
    print("  4. Agent generates formatted response")
    print("  5. Email sent via Gmail API (would send if configured)")

    await db_service.disconnect()
    kafka_producer.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run the test:**
```bash
python test_email.py
```

**Check the Kafka Consumer logs (Terminal 2):**
- Should show agent processing
- Knowledge base search results
- Ticket creation
- Response generation

**Verify in database:**
```bash
docker exec -it customer-success-postgres psql -U postgres -d customer_success

# Check customers
SELECT * FROM customers WHERE primary_email = 'johndoe@example.com';

# Check tickets
SELECT id, source_channel, status, category FROM tickets;

# Check messages
SELECT channel, direction, content FROM messages ORDER BY created_at DESC LIMIT 3;

# Exit
\q
```

---

## Success Criteria ✅

Your deployment is successful when:

- [ ] Docker Desktop is running
- [ ] PostgreSQL container is healthy
- [ ] Kafka container is healthy
- [ ] Database has 7 tables
- [ ] Knowledge base has 10 articles
- [ ] 10 Kafka topics exist (all starting with `fte.`)
- [ ] FastAPI `/health` returns 200
- [ ] FastAPI `/ready` shows database+kafka connected
- [ ] Kafka consumer is listening for messages
- [ ] Test message publishes successfully
- [ ] Consumer processes message (check logs)
- [ ] Customer and ticket appear in database

---

## Troubleshooting

### Problem: Docker Desktop not starting
**Solution:**
- Restart Docker Desktop application
- Check Windows Services: "Docker Desktop Service" should be running
- Restart computer if needed

### Problem: `deploy.sh` fails with "OPENAI_API_KEY not set"
**Solution:**
- Edit `backend/.env`
- Add your actual OpenAI API key
- Save and re-run `./scripts/deploy.sh`

### Problem: Kafka consumer not processing messages
**Solution:**
1. Check consumer is running (Terminal 2)
2. Check Kafka topics exist:
   ```bash
   docker exec customer-success-kafka kafka-topics.sh --list --bootstrap-server localhost:9092 | grep fte
   ```
3. Restart consumer: Ctrl+C and re-run

### Problem: Database connection error
**Solution:**
- Check PostgreSQL is running: `docker ps | grep postgres`
- Check DATABASE_URL in `backend/.env`
- Try: `docker-compose -f infrastructure/docker-compose.yml restart postgres`

---

## What Happens After Testing

Once Phase 3 testing is complete, you have **3 options**:

### Option 1: Complete P1 MVP (Recommended) ⭐
**Goal:** Add WhatsApp support to have a full dual-channel MVP

**Next:** Implement Phase 4 (WhatsApp Support - 14 tasks)
- Similar to email but for WhatsApp
- Twilio integration
- Conversational tone formatting
- Can be done in parallel with testing

**Benefit:** Complete P1 MVP with both priority channels

### Option 2: Production Deployment 🚀
**Goal:** Deploy Phase 3 to production environment

**Next Steps:**
1. Set up Gmail Pub/Sub on Google Cloud (see `infrastructure/kubernetes/configmaps/gmail-config.yaml`)
2. Deploy to Kubernetes cluster
3. Configure production secrets
4. Set up monitoring/alerting
5. Test with real emails

**Benefit:** Get email support live in production

### Option 3: Expand Features 📈
**Goal:** Add more capabilities before production

**Next:** Implement Phase 5 (Web Form) or Phase 6 (Cross-Channel Continuity)

**Benefit:** More features before going live

---

## Time Estimates

- **Docker Desktop setup:** 2 minutes
- **OpenAI API key setup:** 1 minute
- **Run deploy.sh:** 5 minutes
- **Start services:** 1 minute
- **Verification & testing:** 5 minutes

**Total: ~15 minutes to fully deployed and tested Phase 3**

---

## Support Resources

- **Full deployment guide:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Testing guide:** [docs/TESTING.md](docs/TESTING.md)
- **Quick status check:** `./scripts/check_status.sh`
- **View logs:** `docker-compose -f infrastructure/docker-compose.yml logs -f`

---

## Ready to Start?

1. ✅ Start Docker Desktop
2. ✅ Set OPENAI_API_KEY in backend/.env
3. ✅ Run `./scripts/deploy.sh`
4. ✅ Start FastAPI and Kafka consumer
5. ✅ Run test script
6. ✅ Verify in database

**Let's deploy! 🚀**
