# API Keys & Credentials Guide

Complete reference for obtaining all API keys and credentials needed for the Customer Success Digital FTE system.

---

## Overview

| Service | Required? | Purpose | Free Tier? | Estimated Cost |
|---------|-----------|---------|------------|----------------|
| **OpenAI** | ✅ Yes | AI Agent, Embeddings | No | $0.02-0.05/conversation |
| **Twilio** | Optional | WhatsApp Support | Yes ($15 credit) | $0.005/message |
| **Gmail API** | Optional | Email Support | Yes (free) | Free |
| **DigitalOcean** | Optional | Cloud Hosting | No | $48-96/month |

**Minimum to get started:** Just OpenAI API key ($20 credit recommended)

---

## 1. OpenAI API Key (Required) ⭐

### Purpose
- Powers the AI customer support agent (GPT-4 Turbo)
- Generates text embeddings for knowledge base search
- Semantic understanding and response generation

### How to Get It

1. **Sign Up / Log In**
   - Go to: [platform.openai.com](https://platform.openai.com)
   - Click "Sign up" or "Log in"
   - Verify your email and phone number

2. **Add Billing (Required)**
   - Navigate to **Billing** → **Payment methods**
   - Add a credit card
   - Set a spending limit (recommended: $20/month for testing, $100/month for production)

3. **Create API Key**
   - Go to **API keys** (left sidebar)
   - Click **"+ Create new secret key"**
   - Name it: "Customer Success FTE - Production"
   - Copy the key immediately (starts with `sk-proj-...`)
   - **IMPORTANT:** You won't be able to see it again!

4. **Save in Environment File**
   ```bash
   # In backend/.env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Pricing

| Model | Usage | Cost per Call | Estimated Monthly |
|-------|-------|---------------|-------------------|
| GPT-4 Turbo | Agent responses | $0.01-0.03 | $50-200 (1000 conversations) |
| text-embedding-3-small | Knowledge base | $0.00002 per 1K tokens | $1-5 |

**Free tier:** None (pay-as-you-go from $0)

**Recommended starting credit:** $20 for testing, $100+ for production

### Troubleshooting

**"Insufficient quota" error:**
- Solution: Add payment method and wait 5-10 minutes
- New accounts may have rate limits for first 48 hours

**"Invalid API key" error:**
- Double-check you copied the entire key (including `sk-proj-` prefix)
- Ensure no extra spaces before/after the key
- Verify key hasn't been revoked in OpenAI dashboard

---

## 2. Twilio API (Optional - For WhatsApp Support)

### Purpose
- Receive WhatsApp messages from customers
- Send WhatsApp responses via Twilio API
- Track message delivery status

### How to Get It

1. **Sign Up for Free Trial**
   - Go to: [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
   - Enter email, create password
   - Verify phone number and email
   - **You get $15 free credit** (enough for ~3000 WhatsApp messages)

2. **Get Account Credentials**
   - Once logged in to [Twilio Console](https://console.twilio.com):
   - **Account SID**: Shown on dashboard (starts with `AC...`)
   - **Auth Token**: Click "show" to reveal (hidden by default)
   - Copy both values

3. **Enable WhatsApp Sandbox**
   - Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
   - Follow the instructions to join sandbox:
     - Open WhatsApp on your phone
     - Send the join code (e.g., "join yellow-tiger") to the sandbox number
   - Copy the **Sandbox WhatsApp Number** (e.g., `+1 415 523 8886`)

4. **Save Credentials**
   ```bash
   # In backend/.env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

5. **Configure Webhook (After Deployment)**
   - In Twilio Console → **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
   - Set "When a message comes in" to:
     ```
     https://your-domain.com/webhooks/twilio/whatsapp
     ```
   - HTTP Method: **POST**

### Pricing

| Feature | Sandbox (Free Trial) | Production |
|---------|----------------------|------------|
| WhatsApp messages | $0.005/message | $0.005/message |
| Phone number | Free sandbox | $1.15/month |
| Free credit | $15 (~3000 messages) | Pay-as-you-go |

**For production WhatsApp Business API:**
- Apply at: [twilio.com/whatsapp/request-access](https://www.twilio.com/whatsapp/request-access)
- Requires business verification (3-7 days)
- Must have a registered business

### Troubleshooting

**Can't send messages in sandbox:**
- Ensure you've joined the sandbox by sending the join code via WhatsApp
- Only numbers that have joined can receive messages in sandbox mode

**Webhook not receiving messages:**
- Check webhook URL is publicly accessible (not localhost)
- Verify webhook signature validation is working
- Check Twilio debugger: https://console.twilio.com/debugger

---

## 3. Gmail API (Optional - For Email Support)

### Purpose
- Receive incoming customer emails via Gmail Pub/Sub
- Send email responses using Gmail API
- Track email threads for conversation continuity

### How to Get It

1. **Create Google Cloud Project**
   - Go to: [console.cloud.google.com](https://console.cloud.google.com)
   - Click **Select a project** → **New Project**
   - Name: "Customer Success FTE"
   - Click **Create**

2. **Enable Gmail API**
   - In the project, go to **APIs & Services** → **Library**
   - Search: "Gmail API"
   - Click **Gmail API** → **Enable**

3. **Create Service Account**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **Service Account**
   - Service account name: "gmail-webhook-handler"
   - Click **Create and Continue**
   - Grant role: **Project** → **Editor**
   - Click **Continue** → **Done**

4. **Generate JSON Key**
   - Click on the newly created service account
   - Go to **Keys** tab
   - Click **Add Key** → **Create new key**
   - Choose **JSON** format
   - Click **Create**
   - JSON file will download automatically

5. **Save Credentials**
   ```bash
   # Move the downloaded file to your project
   mkdir -p backend/credentials
   mv ~/Downloads/customer-success-fte-*.json backend/credentials/gmail-service-account.json

   # In backend/.env
   GMAIL_SERVICE_ACCOUNT_PATH=./credentials/gmail-service-account.json
   GMAIL_SUPPORT_EMAIL=support@yourdomain.com
   ```

6. **Set Up Gmail Pub/Sub (For Webhooks)**

   a. **Enable Cloud Pub/Sub API**
   - In Google Cloud Console → **APIs & Services** → **Library**
   - Search: "Cloud Pub/Sub API"
   - Click **Enable**

   b. **Create Pub/Sub Topic**
   ```bash
   # Install gcloud CLI: https://cloud.google.com/sdk/docs/install
   gcloud auth login

   # Create topic
   gcloud pubsub topics create gmail-notifications

   # Grant Gmail permission to publish
   gcloud pubsub topics add-iam-policy-binding gmail-notifications \
     --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
     --role=roles/pubsub.publisher
   ```

   c. **Create Push Subscription**
   ```bash
   gcloud pubsub subscriptions create gmail-push-subscription \
     --topic=gmail-notifications \
     --push-endpoint=https://your-domain.com/webhooks/gmail \
     --ack-deadline=30
   ```

   d. **Set Up Gmail Watch**
   - This requires calling Gmail API to "watch" the inbox
   - See: [Gmail API Push Notifications](https://developers.google.com/gmail/api/guides/push)

### Pricing

**Gmail API:** Free (no cost)

**Cloud Pub/Sub:**
- First 10 GB/month: Free
- Beyond 10 GB: $0.06/GB
- **Estimated cost:** $0-2/month for typical usage

### Troubleshooting

**"Service account does not have permission" error:**
- Ensure service account has Editor role
- Grant domain-wide delegation if using Google Workspace

**Pub/Sub not receiving messages:**
- Verify Gmail watch is active (expires after 7 days, must renew)
- Check Pub/Sub subscription is configured correctly
- Test with: `gcloud pubsub subscriptions pull gmail-push-subscription --auto-ack`

---

## 4. DigitalOcean (Optional - For Cloud Deployment)

### Purpose
- Host Kubernetes cluster for production deployment
- Managed PostgreSQL, Load Balancer, Container Registry
- Best price/performance ratio for startups

### How to Get It

1. **Sign Up**
   - Go to: [digitalocean.com](https://www.digitalocean.com)
   - Sign up with email or GitHub
   - **Get $200 free credit** with special promotions (check for current offers)

2. **Create API Token**
   - Go to **API** (left sidebar)
   - Click **Generate New Token**
   - Name: "Customer Success FTE Deployment"
   - Scopes: **Read and Write**
   - Copy the token (starts with `dop_v1_...`)

3. **Save Credentials**
   ```bash
   # For doctl CLI
   doctl auth init
   # Paste your API token when prompted
   ```

4. **Set Up Billing**
   - Add payment method (required after free credit expires)
   - Set billing alerts (recommended: $50, $100 thresholds)

### Pricing

| Resource | Specs | Monthly Cost |
|----------|-------|--------------|
| **Kubernetes** | 3 nodes, 2vCPU, 4GB RAM each | $36 |
| **Load Balancer** | For API service | $12 |
| **Container Registry** | Basic plan | $5 |
| **Total** | Minimum production setup | **$53/month** |

**With autoscaling (3-6 nodes):** $53-106/month

**Free credit:** $200 for 60 days (with promo code)

### Alternatives

**Google Cloud (GKE):**
- Free tier: $300 credit for 90 days
- Cost: $80-150/month after
- Get started: [cloud.google.com/free](https://cloud.google.com/free)

**AWS (EKS):**
- Free tier: Limited (12 months)
- Cost: $75-120/month
- Get started: [aws.amazon.com/free](https://aws.amazon.com/free)

**Azure (AKS):**
- Free tier: $200 credit for 30 days
- Cost: $70-130/month after
- Get started: [azure.microsoft.com/free](https://azure.microsoft.com/free)

---

## Quick Start Checklist

### Minimum Setup (Local Development)

- [ ] OpenAI API key obtained ($20 credit recommended)
- [ ] Docker Desktop installed and running
- [ ] Environment file created at `backend/.env` with OpenAI key
- [ ] Ready to deploy locally with `./deploy.sh`

**Cost:** $0-5 for testing (OpenAI usage only)

---

### Full Production Setup

- [ ] OpenAI API key obtained ($100+ credit)
- [ ] Twilio account created + WhatsApp sandbox configured
- [ ] Gmail API + Pub/Sub set up for email support
- [ ] Cloud platform account created (DigitalOcean recommended)
- [ ] Domain name purchased (optional, ~$12/year)
- [ ] TLS certificate configured (free with Let's Encrypt)
- [ ] Webhook URLs configured in Twilio and Gmail
- [ ] Monitoring set up (Prometheus + Grafana)

**Cost:** $70-120/month (cloud hosting + API usage)

---

## Security Best Practices

### Never Commit API Keys to Git

```bash
# Add to .gitignore
echo "backend/.env" >> .gitignore
echo "backend/credentials/" >> .gitignore
```

### Use Environment Variables

```bash
# Always load from .env file
export $(cat backend/.env | xargs)
```

### Rotate Keys Regularly

- OpenAI: Rotate every 90 days
- Twilio: Rotate every 6 months
- Gmail: Rotate service account keys annually

### Use Kubernetes Secrets (Production)

```bash
# Never store secrets in ConfigMaps or plain YAML
kubectl create secret generic openai-api-key --from-literal=OPENAI_API_KEY='sk-...'

# View secrets (base64 encoded)
kubectl get secret openai-api-key -o yaml
```

---

## Troubleshooting Common Issues

### "Authentication failed" errors

**OpenAI:**
```bash
# Test your key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-proj-YOUR-KEY-HERE"

# Should return list of available models
```

**Twilio:**
```bash
# Test credentials
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"

# Should return account information
```

### Environment variables not loading

```bash
# Check if .env file exists
ls -la backend/.env

# Load manually
export $(cat backend/.env | xargs)

# Verify
echo $OPENAI_API_KEY
```

### Webhook signature validation failing

```bash
# For Twilio: Ensure auth token is correct
# For Gmail: Verify JWT token in Cloud Console matches

# Test webhook locally with ngrok
ngrok http 8000
# Use ngrok URL in webhook configuration
```

---

## Cost Estimation Calculator

### Monthly Costs (Production)

| Component | Volume | Unit Cost | Monthly Total |
|-----------|--------|-----------|---------------|
| OpenAI GPT-4 | 1000 conversations | $0.03/conversation | $30 |
| OpenAI Embeddings | 100K tokens | $0.02/100K | $2 |
| Twilio WhatsApp | 5000 messages | $0.005/message | $25 |
| Gmail API | Any | Free | $0 |
| DigitalOcean K8s | 3-6 nodes | $53-106 | $80 (avg) |
| **Total** | | | **~$137/month** |

### Development/Testing

| Component | Volume | Monthly Total |
|-----------|--------|---------------|
| OpenAI | 100 test conversations | $3 |
| Twilio | $15 free credit | $0 |
| Gmail | Free tier | $0 |
| Local (Docker) | No hosting | $0 |
| **Total** | | **~$3/month** |

---

## Next Steps

1. **For Local Testing:**
   - Get OpenAI API key only
   - Follow: [DEPLOY_LOCAL.md](DEPLOY_LOCAL.md)

2. **For Production:**
   - Get all API keys from this guide
   - Follow: [DEPLOY_CLOUD.md](DEPLOY_CLOUD.md)

3. **For Enterprise:**
   - Contact OpenAI for volume pricing
   - Apply for Twilio WhatsApp Business API
   - Set up Google Workspace integration

---

## Support Resources

- **OpenAI**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Twilio**: [twilio.com/docs/whatsapp](https://www.twilio.com/docs/whatsapp)
- **Gmail API**: [developers.google.com/gmail/api](https://developers.google.com/gmail/api)
- **DigitalOcean**: [docs.digitalocean.com/products/kubernetes](https://docs.digitalocean.com/products/kubernetes/)

---

**Ready to deploy?** Start with local development using just your OpenAI API key!
