# Local Deployment Guide (Minikube)

Complete guide for deploying Customer Success Digital FTE to local Kubernetes cluster.

## Prerequisites

- Docker Desktop (running)
- kubectl CLI
- Minikube
- OpenAI API Key (required)
- Twilio credentials (optional, for WhatsApp)
- Gmail service account (optional, for Email)

---

## Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verify cluster is running
kubectl get nodes
# Should show: minikube   Ready   control-plane   <age>
```

---

## Step 2: Create Kubernetes Secrets

### OpenAI API Key (Required)

```bash
kubectl create secret generic openai-api-key \
  --from-literal=OPENAI_API_KEY='sk-proj-your-actual-key-here'
```

### Twilio Credentials (Optional - for WhatsApp)

```bash
kubectl create secret generic twilio-credentials \
  --from-literal=TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxx' \
  --from-literal=TWILIO_AUTH_TOKEN='your-auth-token' \
  --from-literal=TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'
```

### Database Credentials

```bash
kubectl create secret generic database-credentials \
  --from-literal=POSTGRES_USER='postgres' \
  --from-literal=POSTGRES_PASSWORD='secure-password-here' \
  --from-literal=DATABASE_URL='postgresql+asyncpg://postgres:secure-password-here@postgresql-service:5432/customer_success'
```

### Gmail Service Account (Optional - for Email)

```bash
# If you have the service account JSON file
kubectl create secret generic gmail-service-account \
  --from-file=gmail-service-account.json=backend/credentials/gmail-service-account.json
```

---

## Step 3: Build Docker Images

```bash
# Build backend image
cd backend
docker build -t customer-success-api:latest .

# Build frontend image
cd ../frontend
docker build -t customer-success-frontend:latest .

# Load images into Minikube
minikube image load customer-success-api:latest
minikube image load customer-success-frontend:latest
```

---

## Step 4: Deploy Infrastructure Components

### Deploy PostgreSQL

```bash
kubectl apply -f infrastructure/kubernetes/deployments/postgresql.yaml
kubectl apply -f infrastructure/kubernetes/services/postgresql-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s

# Initialize database schema
cat database/schema.sql | kubectl exec -i postgresql-0 -- psql -U postgres -d customer_success
```

### Deploy Kafka

```bash
kubectl apply -f infrastructure/kubernetes/deployments/kafka.yaml

# Wait for all Kafka brokers to be ready
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s

# Create Kafka topics
kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.tickets.incoming --partitions 12 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.channels.email.inbound --partitions 6 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.channels.email.outbound --partitions 6 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.channels.whatsapp.inbound --partitions 6 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.channels.whatsapp.outbound --partitions 6 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.channels.webform.inbound --partitions 6 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.escalations --partitions 3 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.dlq --partitions 3 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.agent.responses --partitions 3 --replication-factor 3

kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic fte.analytics.sentiment --partitions 3 --replication-factor 3
```

---

## Step 5: Deploy Application Services

### Deploy ConfigMap

```bash
kubectl apply -f infrastructure/kubernetes/configmaps/app-config.yaml
```

### Deploy API Service

```bash
kubectl apply -f infrastructure/kubernetes/deployments/api.yaml
kubectl apply -f infrastructure/kubernetes/services/api-service.yaml

# Wait for API to be ready
kubectl wait --for=condition=ready pod -l app=customer-success-api --timeout=300s
```

### Deploy Agent Workers

```bash
kubectl apply -f infrastructure/kubernetes/deployments/agent-workers.yaml

# Wait for workers to be ready
kubectl wait --for=condition=ready pod -l app=agent-workers --timeout=300s
```

---

## Step 6: Seed Knowledge Base

```bash
# Port-forward to PostgreSQL
kubectl port-forward svc/postgresql-service 5432:5432 &

# Run seeding script (from project root)
cd scripts
python seed_knowledge_base.py

# Stop port-forward
kill %1
```

---

## Step 7: Set Up KEDA Autoscaling (Optional)

```bash
# Install KEDA
kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml

# Wait for KEDA to be ready
kubectl wait --for=condition=ready pod -l app=keda-operator -n keda --timeout=300s

# Apply ScaledObject for agent workers
kubectl apply -f infrastructure/kubernetes/hpa/keda-scaledobject.yaml
```

---

## Step 8: Expose Services Locally

### API Service

```bash
# Get the LoadBalancer URL (Minikube tunnel required)
minikube tunnel

# In another terminal, get the external IP
kubectl get svc api-service
# EXTERNAL-IP will be shown (e.g., 127.0.0.1)
```

Your API is now available at:
- **Health Check**: http://127.0.0.1/health
- **Readiness Check**: http://127.0.0.1/ready
- **Metrics**: http://127.0.0.1/metrics
- **API Docs**: http://127.0.0.1/docs

### Frontend (if deployed)

```bash
kubectl port-forward svc/frontend-service 3000:3000

# Access at http://localhost:3000
```

---

## Step 9: Verify Deployment

### Check All Pods

```bash
kubectl get pods

# Expected output:
# NAME                                   READY   STATUS    RESTARTS   AGE
# postgresql-0                           1/1     Running   0          10m
# kafka-0                                1/1     Running   0          8m
# kafka-1                                1/1     Running   0          8m
# kafka-2                                1/1     Running   0          8m
# customer-success-api-xxxxxxxxxx-xxxxx  1/1     Running   0          5m
# customer-success-api-xxxxxxxxxx-xxxxx  1/1     Running   0          5m
# customer-success-api-xxxxxxxxxx-xxxxx  1/1     Running   0          5m
# agent-workers-xxxxxxxxxx-xxxxx         1/1     Running   0          3m
# agent-workers-xxxxxxxxxx-xxxxx         1/1     Running   0          3m
```

### Check Services

```bash
kubectl get svc

# Expected output:
# NAME                   TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)
# api-service            LoadBalancer   10.96.xxx.xxx    127.0.0.1     80:xxxxx/TCP
# postgresql-service     ClusterIP      10.96.xxx.xxx    <none>        5432/TCP
# kafka-service          ClusterIP      10.96.xxx.xxx    <none>        9092/TCP
```

### Test Health Endpoint

```bash
curl http://127.0.0.1/health

# Expected response:
# {"status":"healthy","timestamp":"2026-02-01T..."}
```

### View Logs

```bash
# API logs
kubectl logs -l app=customer-success-api --tail=50 -f

# Worker logs
kubectl logs -l app=agent-workers --tail=50 -f

# Kafka logs
kubectl logs kafka-0 --tail=50
```

---

## Step 10: Test End-to-End

### Submit Test Web Form Request

```bash
curl -X POST http://127.0.0.1/api/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Password Reset Help",
    "message": "How do I reset my password?",
    "priority": "normal"
  }'

# Expected response:
# {
#   "ticket_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "status": "received",
#   "message": "Your support request has been received. We'll respond within 10 minutes."
# }
```

### Check Ticket Processing

```bash
# Watch worker logs
kubectl logs -l app=agent-workers --tail=100 -f

# Should show:
# - Message consumed from Kafka
# - AI agent processing
# - Knowledge base search
# - Response generated
```

### Query Database

```bash
kubectl exec -it postgresql-0 -- psql -U postgres -d customer_success

# Run queries:
SELECT COUNT(*) FROM tickets;
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM customers;

# Exit:
\q
```

---

## Cleanup

To stop and remove everything:

```bash
# Delete all Kubernetes resources
kubectl delete -f infrastructure/kubernetes/deployments/
kubectl delete -f infrastructure/kubernetes/services/
kubectl delete -f infrastructure/kubernetes/configmaps/
kubectl delete -f infrastructure/kubernetes/hpa/
kubectl delete secrets --all

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod details
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# 1. ImagePullBackOff → Images not loaded into Minikube
#    Solution: minikube image load <image-name>
# 2. CrashLoopBackOff → Check logs for errors
# 3. Secrets not found → Recreate secrets
```

### API Not Accessible

```bash
# Ensure minikube tunnel is running
minikube tunnel

# Check service
kubectl get svc api-service

# Port forward as alternative
kubectl port-forward svc/api-service 8000:80
# Access at http://localhost:8000
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
kubectl get pods -l app=postgresql

# Check database logs
kubectl logs postgresql-0

# Test connection
kubectl exec -it postgresql-0 -- psql -U postgres -c "SELECT 1;"
```

### Kafka Connection Errors

```bash
# Verify Kafka brokers
kubectl get pods -l app=kafka

# List topics
kubectl exec -it kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check consumer groups
kubectl exec -it kafka-0 -- kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

---

## Next Steps

1. **Configure Webhooks**: Once you have a public URL (ngrok, LoadBalancer), configure:
   - Twilio WhatsApp webhook → `https://your-domain.com/webhooks/twilio/whatsapp`
   - Gmail Pub/Sub push endpoint → `https://your-domain.com/webhooks/gmail`

2. **Monitor Metrics**: Access Prometheus metrics at `/metrics` endpoint

3. **Scale Workers**: KEDA will automatically scale based on Kafka lag

4. **Production Deployment**: See docs/DEPLOY_CLOUD.md for cloud platform deployment

---

**Deployment Complete!** 🎉

Your Customer Success Digital FTE is now running on local Kubernetes.
