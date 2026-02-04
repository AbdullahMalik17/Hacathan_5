# Complete Deployment Guide: Customer Success Digital FTE

This guide provides a complete step-by-step process to deploy the Customer Success Digital FTE project with the frontend on Vercel and backend on DigitalOcean.

## Overview

The Customer Success Digital FTE is an AI-powered customer support agent that handles inquiries across Email, WhatsApp, and Web Form channels. The architecture consists of:

- **Frontend**: Next.js application hosted on Vercel
- **Backend**: FastAPI application with Kafka and PostgreSQL, hosted on DigitalOcean Kubernetes
- **AI Component**: OpenAI GPT-4 Turbo for customer support automation
- **Message Queue**: Apache Kafka for reliable message processing
- **Database**: PostgreSQL with pgvector for semantic search

## Prerequisites

Before starting the deployment, ensure you have:

1. **Accounts**:
   - DigitalOcean account with billing set up
   - Vercel account (free tier available)
   - OpenAI account with API key
   - (Optional) Twilio account for WhatsApp integration
   - (Optional) Google Cloud account for Gmail integration

2. **Tools**:
   - `doctl` (DigitalOcean CLI)
   - `vercel` CLI (install with `npm i -g vercel`)
   - `kubectl`
   - `docker`

3. **API Keys**:
   - OpenAI API Key (required)
   - Twilio credentials (optional)
   - Gmail service account (optional)

## Step 1: Prepare Your Local Environment

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd hacathan_5
   ```

2. Navigate to the project directory and ensure you have the complete project structure:
   ```
   hacathan_5/
   ├── backend/
   ├── frontend/
   ├── infrastructure/
   ├── database/
   ├── scripts/
   └── docs/
   ```

## Step 2: Deploy the Backend to DigitalOcean

### 2.1: Create DigitalOcean Resources

1. **Authenticate with DigitalOcean**:
   ```bash
   doctl auth init
   # Enter your DigitalOcean API token
   ```

2. **Create Kubernetes cluster**:
   ```bash
   doctl kubernetes cluster create customer-success-prod \
     --region nyc1 \
     --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=3;max-nodes=6" \
     --wait
   ```

3. **Configure kubectl**:
   ```bash
   doctl kubernetes cluster kubeconfig save customer-success-prod
   kubectl get nodes
   ```

### 2.2: Set Up Container Registry

1. **Create DigitalOcean Container Registry**:
   ```bash
   doctl registry create customer-success-registry
   doctl registry login
   ```

2. **Build and push backend images**:
   ```bash
   # Build API image
   cd backend
   docker build -t registry.digitalocean.com/customer-success-registry/api:latest .
   
   # Build worker image (if separate)
   docker build -t registry.digitalocean.com/customer-success-registry/worker:latest . --target worker
   
   # Push images
   docker push registry.digitalocean.com/customer-success-registry/api:latest
   docker push registry.digitalocean.com/customer-success-registry/worker:latest
   
   # Connect registry to cluster
   doctl kubernetes cluster registry add customer-success-prod
   ```

### 2.3: Configure Secrets

1. **Create required secrets**:
   ```bash
   # OpenAI API Key and other API keys
   kubectl create secret generic api-keys \
     --from-literal=openai-api-key='sk-proj-your-actual-openai-key-here' \
     --from-literal=twilio-account-sid='ACxxxxxxxxxxxx' \
     --from-literal=twilio-auth-token='your-twilio-auth-token'
   
   # Database credentials
   kubectl create secret generic database-credentials \
     --from-literal=database-url='postgresql+asyncpg://postgres:YOUR_STRONG_PASSWORD@postgresql-service:5432/customer_success' \
     --from-literal=username='postgres' \
     --from-literal=password='YOUR_STRONG_PASSWORD'
   
   # Gmail credentials (if using Gmail integration)
   kubectl create secret generic gmail-credentials \
     --from-file=gmail-service-account.json=/path/to/your/gmail-service-account.json
   ```

### 2.4: Deploy Infrastructure

1. **Deploy PostgreSQL and Kafka**:
   ```bash
   cd ../infrastructure/kubernetes
   
   # Deploy PostgreSQL
   kubectl apply -f deployments/postgresql.yaml
   kubectl apply -f services/postgresql-service.yaml
   kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s
   
   # Deploy Kafka
   kubectl apply -f deployments/kafka.yaml
   kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
   
   # Create Kafka topics
   kubectl exec -it kafka-0 -- /bin/bash -c '
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.tickets.incoming --partitions 12 --replication-factor 3
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.email.inbound --partitions 6 --replication-factor 3
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.whatsapp.inbound --partitions 6 --replication-factor 3
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.webform.inbound --partitions 6 --replication-factor 3
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.escalations --partitions 3 --replication-factor 3
     kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.dlq --partitions 3 --replication-factor 3
   '
   ```

### 2.5: Deploy Application

1. **Deploy the API and workers**:
   ```bash
   # Deploy ConfigMap
   kubectl apply -f ../configmaps/app-config.yaml
   
   # Update image references in deployment files
   sed -i 's|customer-success-fte/api:latest|registry.digitalocean.com/customer-success-registry/api:latest|g' deployments/api.yaml
   sed -i 's|customer-success-fte/worker:latest|registry.digitalocean.com/customer-success-registry/worker:latest|g' deployments/agent-workers.yaml
   
   # Deploy API
   kubectl apply -f deployments/api.yaml
   kubectl apply -f services/api-service.yaml
   kubectl wait --for=condition=ready pod -l app=customer-success-fte,component=api --timeout=300s
   
   # Deploy Workers
   kubectl apply -f deployments/agent-workers.yaml
   kubectl wait --for=condition=ready pod -l app=customer-success-fte,component=agent-workers --timeout=300s
   ```

### 2.6: Get Backend URL

1. **Get the LoadBalancer IP**:
   ```bash
   kubectl get svc customer-success-api-service -w
   # Note the EXTERNAL-IP assigned to your service
   ```

2. **Test the backend**:
   ```bash
   export BACKEND_API_URL=your-external-ip
   curl http://$BACKEND_API_URL/health
   ```

### 2.7: Install KEDA for Auto-scaling

1. **Install KEDA**:
   ```bash
   kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml
   kubectl wait --for=condition=ready pod -l app=keda-operator -n keda --timeout=300s
   kubectl apply -f ../hpa/keda-scaledobject.yaml
   ```

## Step 3: Deploy the Frontend to Vercel

### 3.1: Prepare Frontend for Deployment

1. **Navigate to frontend directory**:
   ```bash
   cd ../../frontend
   ```

2. **Ensure vercel.json exists** (already created in this project):
   ```json
   {
     "version": 2,
     "framework": "nextjs",
     "env": {
       "NEXT_PUBLIC_API_URL": "https://your-backend-domain.com"
     }
   }
   ```

### 3.2: Deploy to Vercel

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy the frontend**:
   ```bash
   # For production deployment
   vercel --prod
   
   # Or for staging first
   vercel
   ```

3. **Set environment variables in Vercel dashboard**:
   - Go to your Vercel dashboard
   - Select your project
   - Go to Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` with value as your backend API URL (from Step 2.6)

### 3.3: Link to Git Repository (Recommended)

1. **Connect to Git**:
   - Push your code to GitHub/GitLab/Bitbucket
   - In Vercel dashboard, click "Import Project"
   - Select your repository
   - Add environment variables as above
   - Deploy

## Step 4: Configure Webhooks

Once both deployments are complete, configure the webhooks:

### 4.1: Twilio WhatsApp Webhook

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
3. Set "When a message comes in" to:
   ```
   https://your-vercel-domain.com/api/webhooks/twilio/whatsapp
   ```
   Or if using direct backend access:
   ```
   https://your-backend-domain.com/webhooks/twilio/whatsapp
   ```

### 4.2: Gmail Pub/Sub Push

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Pub/Sub** → **Topics** → `gmail-notifications`
3. Create a subscription:
   - Name: `gmail-push-subscription`
   - Delivery type: **Push**
   - Endpoint URL: `https://your-backend-domain.com/webhooks/gmail`

## Step 5: Seed Knowledge Base

1. **Run the seeding script**:
   ```bash
   # From your local machine, with kubectl configured
   cd ../scripts
   
   # Port-forward to PostgreSQL
   kubectl port-forward svc/postgresql-service 5432:5432 &
   
   # Run seeding script
   python seed_knowledge_base.py
   
   # Stop port-forward
   kill %1
   ```

## Step 6: Verification and Testing

### 6.1: Check All Components

1. **Verify all pods are running**:
   ```bash
   kubectl get pods
   ```

2. **Check services**:
   ```bash
   kubectl get svc
   ```

3. **View logs**:
   ```bash
   kubectl logs -l app=customer-success-fte,component=api --tail=50
   kubectl logs -l app=customer-success-fte,component=agent-workers --tail=50
   ```

### 6.2: Test the API

1. **Health check**:
   ```bash
   curl https://your-backend-domain.com/health
   ```

2. **Submit a test support request**:
   ```bash
   curl -X POST https://your-backend-domain.com/api/support/submit \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "email": "test@example.com",
       "subject": "Test Inquiry",
       "message": "This is a test message to verify the system is working.",
       "priority": "normal"
     }'
   ```

### 6.3: Test the Frontend

1. Visit your Vercel deployment URL
2. Submit a support request through the web form
3. Verify the request is processed by checking backend logs

## Step 7: Production Hardening

### 7.1: Security Enhancements

1. **Enable TLS/HTTPS**:
   - Configure cert-manager with Let's Encrypt
   - Update ingress to use TLS

2. **Set up monitoring**:
   - Install Prometheus and Grafana
   - Configure alerts for critical metrics

3. **Database backups**:
   - Set up automated PostgreSQL backups

### 7.2: Performance Optimizations

1. **Resource limits**:
   - Fine-tune CPU and memory limits based on usage

2. **Auto-scaling**:
   - Adjust KEDA scaling parameters based on load

3. **Caching**:
   - Implement Redis for caching if needed

## Troubleshooting

### Common Issues

1. **Backend not accessible**:
   - Check LoadBalancer service status: `kubectl get svc`
   - Verify firewall rules allow traffic

2. **Frontend can't connect to backend**:
   - Verify `NEXT_PUBLIC_API_URL` is correctly set
   - Check CORS settings in backend

3. **Kafka connectivity issues**:
   - Verify Kafka pods are running: `kubectl get pods -l app=kafka`
   - Check Kafka logs: `kubectl logs kafka-0`

4. **Database connection errors**:
   - Verify database pods are running: `kubectl get pods -l app=postgresql`
   - Check database logs: `kubectl logs postgresql-0`

## Maintenance

### Regular Tasks

1. **Monitor resource usage**:
   ```bash
   kubectl top nodes
   kubectl top pods
   ```

2. **Check logs regularly**:
   ```bash
   kubectl logs -l app=customer-success-fte --tail=100
   ```

3. **Update dependencies**:
   - Regularly update backend dependencies
   - Update frontend dependencies
   - Update Kubernetes components

### Scaling

1. **Manual scaling**:
   ```bash
   # Scale API replicas
   kubectl scale deployment customer-success-api --replicas=5
   
   # Scale worker replicas
   kubectl scale deployment customer-success-agent-workers --replicas=4
   ```

2. **Auto-scaling**:
   - Monitor KEDA metrics
   - Adjust scaling parameters as needed

## Cost Optimization

- **DigitalOcean**: $48-96/month depending on usage
- **Vercel**: Free tier for frontend (with usage limits)
- **OpenAI**: Pay-per-use based on API calls
- **Optimization tips**:
  - Use auto-scaling to reduce costs during low traffic
  - Monitor and optimize resource usage
  - Consider reserved instances for predictable workloads

## Conclusion

Your Customer Success Digital FTE is now deployed with:
- Frontend on Vercel (globally distributed)
- Backend on DigitalOcean Kubernetes (scalable and reliable)
- Complete integration across all channels
- Auto-scaling capabilities
- Production-ready architecture

The system is ready to handle customer inquiries across Email, WhatsApp, and Web Form channels using AI-powered responses.