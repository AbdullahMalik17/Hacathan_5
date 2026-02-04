# Azure Deployment Guide (Free Tier)

This guide explains how to deploy the Customer Success Digital FTE to Azure (Backend) and Vercel (Frontend) using free-tier services.

## Architecture

| Service | Provider | Tier |
|---------|----------|------|
| **Frontend** | Vercel | Free Tier |
| **Backend API** | Azure Container Apps | Free Monthly Grant (180k vCPU-s) |
| **Worker Process** | Azure Container Apps | Free Monthly Grant |
| **Database** | Azure Database for PostgreSQL | Flexible Server (12mo Free Trial) |
| **Messaging** | Upstash Kafka | Serverless Free Tier |

---

## 1. Prerequisites

1. **Azure Account**: [azure.microsoft.com/free](https://azure.microsoft.com/free)
2. **Azure CLI**: [Install `az` CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Upstash Account**: [console.upstash.com](https://console.upstash.com/)
4. **Vercel CLI**: `npm i -g vercel`

---

## 2. Infrastructure Setup

### 2.1 Kafka (Upstash)
1. Log in to [Upstash Console](https://console.upstash.com/).
2. Create a **Kafka Cluster** (Type: Serverless).
3. Create a **Topic** named `fte.tickets.incoming` (and others like `fte.dlq`).
4. Copy the following from the "Details" or "Connect" tab:
   - `Bootstrap Endpoint`
   - `SASL Username`
   - `SASL Password`

### 2.2 Database (Azure PostgreSQL)
1. Open Azure Portal and search for "Azure Database for PostgreSQL flexible servers".
2. Create a new server:
   - **Compute + storage**: Select "Burstable, B1ms" (Free trial eligible).
   - **PostgreSQL version**: 16.
   - **Networking**: Allow public access from "Azure services".
3. **Enable pgvector**:
   - Go to "Server parameters" in the sidebar.
   - Search for `azure.extensions`.
   - Add `VECTOR` to the list.
   - Click Save.
4. **Connect and Initialize**:
   - Use a tool like `psql` or Azure Query Editor to run `database/schema.sql`.

---

## 3. Backend Deployment (Azure Container Apps)

We will deploy two separate Container Apps: one for the API and one for the Worker.

### 3.1 Login and Setup

You can use the provided helper script to automate the deployment:

```bash
./deploy_azure.sh
```

Or follow the manual steps below:

```bash
az login
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# Create Resource Group and Environment
az group create --name fte-group --location eastus
az containerapp env create --name fte-env --resource-group fte-group --location eastus
```

### 3.2 Deploy Backend API
```bash
cd backend

# Deploy API
az containerapp up \
  --name fte-api \
  --resource-group fte-group \
  --environment fte-env \
  --source . \
  --ingress external \
  --target-port 8000 \
  --env-vars \
    DATABASE_URL="postgresql://user:pass@host:5432/db" \
    KAFKA_BOOTSTRAP_SERVERS="pkc-xxxx.us-east-1.aws.confluent.cloud:9092" \
    KAFKA_SASL_USERNAME="XXX" \
    KAFKA_SASL_PASSWORD="XXX" \
    OPENAI_API_KEY="sk-xxx" \
    KAFKA_SECURITY_PROTOCOL="SASL_SSL" \
    KAFKA_SASL_MECHANISM="SCRAM-SHA-256"
```

### 3.3 Deploy Worker
```bash
# Deploy Worker (no ingress, custom command)
az containerapp create \
  --name fte-worker \
  --resource-group fte-group \
  --environment fte-env \
  --image <IMAGE_URL_FROM_PREVIOUS_STEP> \
  --command "python" "-m" "src.workers.message_processor" \
  --env-vars \
    DATABASE_URL="..." \
    KAFKA_BOOTSTRAP_SERVERS="..." \
    KAFKA_SASL_USERNAME="..." \
    KAFKA_SASL_PASSWORD="..." \
    OPENAI_API_KEY="..." \
    KAFKA_SECURITY_PROTOCOL="SASL_SSL" \
    KAFKA_SASL_MECHANISM="SCRAM-SHA-256"
```

---

## 4. Code Configuration Updates

The backend has been updated to support SASL authentication for cloud Kafka providers (like Upstash). The following variables are now supported in `backend/src/config.py`:
- `KAFKA_SECURITY_PROTOCOL` (default: `PLAINTEXT`, use `SASL_SSL` for cloud)
- `KAFKA_SASL_MECHANISM` (default: `PLAIN`, use `SCRAM-SHA-256` for Upstash)
- `KAFKA_SASL_USERNAME`
- `KAFKA_SASL_PASSWORD`

---

## 5. Frontend Deployment (Vercel)

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```
2. **Deploy**:
   ```bash
   vercel
   ```
3. **Set Environment Variable**:
   - In Vercel Dashboard -> Settings -> Environment Variables:
   - Add `NEXT_PUBLIC_API_URL` = `https://fte-api.<unique-id>.eastus.azurecontainerapps.io`
4. **Redeploy**:
   ```bash
   vercel --prod
   ```

---

## 5. Environment Variables Reference

| Variable | Description | Source |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | Azure Portal |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka endpoint | Upstash Console |
| `KAFKA_SASL_USERNAME` | Kafka username | Upstash Console |
| `KAFKA_SASL_PASSWORD` | Kafka password | Upstash Console |
| `KAFKA_SECURITY_PROTOCOL` | Set to `SASL_SSL` | Upstash / Confluent |
| `KAFKA_SASL_MECHANISM` | Set to `SCRAM-SHA-256` | Upstash |
| `OPENAI_API_KEY` | OpenAI API Key | OpenAI Dashboard |
| `NEXT_PUBLIC_API_URL` | Frontend link to Backend | Azure API URL |

---

## 6. Verification

1. **Backend Health**: `curl https://fte-api.<...>.azurecontainerapps.io/health`
2. **Logs**: `az containerapp logs show --name fte-api --resource-group fte-group`
3. **Database**: Check `tickets` table after submitting via frontend.
