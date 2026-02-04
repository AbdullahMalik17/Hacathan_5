# Fly.io Deployment Plan

## 1. Prerequisites
- **Fly CLI**: You need to install the Fly.io CLI.
  ```bash
  curl -L https://fly.io/install.sh | sh
  # Add to path as instructed by the installer
  ```
- **Account**: Run `fly auth login` to sign in.

## 2. Architecture Changes for Cloud
Moving from local Docker Compose to Fly.io requires separating services:

| Service | Local (Docker) | Fly.io (Production) |
|---------|----------------|---------------------|
| **Database** | Container (`postgres:15`) | **Fly Managed Postgres** (High Availability, auto-backups) |
| **Messaging** | Container (`kafka`) | **Upstash Kafka** (Serverless, free tier, recommended) OR **Self-hosted Kafka on Fly** (Complex) |
| **Backend** | Container (`backend`) | **Fly App 1** (Python/FastAPI) |
| **Worker** | Container (`worker`) | **Fly App 2** (Python Worker) or Process in App 1 |
| **Frontend** | Container (`frontend`) | **Fly App 3** (Next.js) |

## 3. Step-by-Step Guide

### Step A: Database (Postgres)
We will create a Fly Postgres cluster.
```bash
fly postgres create --name fte-db --region iad --vm-size shared-cpu-1x --initial-cluster-size 1
```
*Note: We need to enable `pgvector` extension manually after creation.*

### Step B: Kafka (Message Broker)
**Recommendation: Use Upstash (Serverless Kafka)**
1. Go to [Upstash Console](https://console.upstash.com/).
2. Create a Kafka Cluster.
3. Get the `Bootstrap Endpoint`, `Username`, and `Password`.
4. We will set these as secrets in our Fly apps.

### Step C: Backend (FastAPI)
1. Create `fly.toml` for the backend.
2. Set secrets:
   ```bash
   fly secrets set DATABASE_URL=... OPENAI_API_KEY=... KAFKA_BOOTSTRAP_SERVERS=... KAFKA_SASL_USERNAME=... KAFKA_SASL_PASSWORD=...
   ```
3. Deploy.

### Step D: Worker (Background Processor)
We can run the worker as a separate "process" within the **same** Fly app as the backend to save money and configuration, or as a separate app.
*Recommendation: Same app, different process.*

### Step E: Frontend (Next.js)
1. Create `fly.toml` for `frontend/`.
2. Deploy.

---

**Does this plan sound good? specifically, are you okay using Upstash for Kafka (easiest), or do you have another preference?**
