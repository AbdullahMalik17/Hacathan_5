# Environment Variables Configuration Guide

This guide explains all the environment variables needed for both frontend and backend deployments.

## Backend Environment Variables

### Required Variables

#### Database Configuration
- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql+asyncpg://username:password@host:port/database`
  - Example: `postgresql+asyncpg://postgres:password@your-db-host:5432/customer_success`
  - **Required for production**

- `DB_POOL_MIN_SIZE`: Minimum database connections (default: 10)
- `DB_POOL_MAX_SIZE`: Maximum database connections (default: 20)
- `DB_QUERY_TIMEOUT`: Query timeout in seconds (default: 30)

#### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key
  - Format: `sk-proj-...`
  - **Required for AI functionality**
  - Get from: https://platform.openai.com/api-keys

#### Kafka Configuration
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
  - Format: `host1:port,host2:port`
  - Example: `kafka-cluster:9092`
  - **Required for message processing**

### Optional Variables

#### Twilio WhatsApp Configuration
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
  - Format: `AC...`
  - Get from: Twilio Console → Account Info
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
  - Get from: Twilio Console → Account Info
- `TWILIO_WHATSAPP_NUMBER`: Your WhatsApp number
  - Format: `whatsapp:+1234567890`

#### Gmail API Configuration
- `GMAIL_SERVICE_ACCOUNT_PATH`: Path to service account JSON file
  - Default: `./credentials/gmail-service-account.json`
- `GMAIL_SUPPORT_EMAIL`: Support email address
  - Format: `support@yourdomain.com`

#### Application Configuration
- `LOG_LEVEL`: Logging level (default: INFO)
  - Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `AGENT_RESPONSE_TIMEOUT`: Timeout for agent responses in seconds (default: 180)
- `CORRELATION_ID_HEADER`: Header name for correlation IDs (default: X-Correlation-ID)

#### Performance Configuration
- `MAX_CONCURRENT_CONVERSATIONS`: Max concurrent conversations (default: 1000)
- `KNOWLEDGE_BASE_SIMILARITY_THRESHOLD`: Similarity threshold for KB search (default: 0.6)
- `MESSAGE_RETRY_MAX_ATTEMPTS`: Max retry attempts for failed messages (default: 5)
- `MESSAGE_RETRY_BACKOFF_FACTOR`: Backoff factor for retries (default: 2)

#### Security Configuration
- `WEBHOOK_SECRET_KEY`: Secret key for webhook validation
  - Generate with: `openssl rand -base64 32`
- `JWT_ALGORITHM`: Algorithm for JWT tokens (default: HS256)

## Frontend Environment Variables

### Required Variables

#### API Configuration
- `NEXT_PUBLIC_API_URL`: Backend API URL
  - Format: `https://your-backend-domain.com`
  - Default: `http://localhost:8000`
  - **Must be set for production**

## Deployment-Specific Configuration

### For DigitalOcean Kubernetes Deployment

#### Backend Secrets (to be created in Kubernetes)
```bash
# API Keys Secret
kubectl create secret generic api-keys \
  --from-literal=openai-api-key='sk-proj-your-actual-key-here' \
  --from-literal=twilio-account-sid='ACxxxxxxxxxxxx' \
  --from-literal=twilio-auth-token='your-auth-token'

# Database Credentials Secret
kubectl create secret generic database-credentials \
  --from-literal=database-url='postgresql+asyncpg://postgres:YOUR_PASSWORD@postgresql-service:5432/customer_success' \
  --from-literal=username='postgres' \
  --from-literal=password='YOUR_PASSWORD'

# Gmail Credentials Secret (if using Gmail)
kubectl create secret generic gmail-credentials \
  --from-file=gmail-service-account.json=/path/to/your/service-account.json
```

#### Frontend Environment on Vercel
Set these in Vercel dashboard under Project Settings → Environment Variables:
- `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., `https://api.yourdomain.com`)

### For Local Development
Create `.env` files in both directories:

#### Backend (.env in /backend/)
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/customer_success
OPENAI_API_KEY=sk-proj-your-key-here
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

#### Frontend (.env.local in /frontend/)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Security Best Practices

1. **Never commit secrets to version control**
2. **Use strong, randomly generated passwords**
3. **Rotate API keys regularly**
4. **Use HTTPS for all production endpoints**
5. **Restrict access to secrets in production**

## Required Services and API Keys

Before deploying, ensure you have:

1. **OpenAI API Key** (required)
   - Go to: https://platform.openai.com/api-keys
   - Required for AI agent functionality

2. **Twilio Account** (optional, for WhatsApp)
   - Go to: https://www.twilio.com
   - Required for WhatsApp integration

3. **Gmail Service Account** (optional, for Email)
   - Go to: Google Cloud Console → APIs & Services → Credentials
   - Required for Gmail integration

4. **Domain Name** (recommended)
   - Required for webhook configurations
   - Needed for production deployment