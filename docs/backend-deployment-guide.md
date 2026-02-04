# Backend Deployment Guide for DigitalOcean

This guide will walk you through deploying the Customer Success Digital FTE backend to DigitalOcean Kubernetes (DOKS).

## Prerequisites

1. **DigitalOcean Account**: Sign up at [digitalocean.com](https://www.digitalocean.com)
2. **doctl CLI**: Install command-line tool
   ```bash
   # macOS
   brew install doctl

   # Linux
   cd /tmp && wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
   tar xf doctl-1.104.0-linux-amd64.tar.gz && sudo mv doctl /usr/local/bin
   ```

3. **Authenticate doctl**:
   ```bash
   doctl auth init
   # Enter your DigitalOcean API token (create at cloud.digitalocean.com/account/api/tokens)
   ```

4. **kubectl**: Install if not already present
   ```bash
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin
   ```

## Step 1: Create Kubernetes Cluster

```bash
# Create a 3-node cluster in NYC region
doctl kubernetes cluster create customer-success-prod \
  --region nyc1 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=3;max-nodes=6" \
  --wait

# This creates:
# - 3 nodes (2 vCPU, 4GB RAM each) = $36/month
# - Auto-scaling 3-6 nodes
# - Load balancer = $12/month
# Total: ~$48-96/month depending on scale
```

## Step 2: Configure kubectl

```bash
# Download kubeconfig
doctl kubernetes cluster kubeconfig save customer-success-prod

# Verify connection
kubectl get nodes
```

## Step 3: Set Up Container Registry

```bash
# Create DigitalOcean Container Registry
doctl registry create customer-success-registry

# Authenticate Docker
doctl registry login

# Build and tag images
cd /path/to/your/project/backend
docker build -t registry.digitalocean.com/customer-success-registry/api:latest .
docker build -t registry.digitalocean.com/customer-success-registry/worker:latest . --target worker

# Push images
docker push registry.digitalocean.com/customer-success-registry/api:latest
docker push registry.digitalocean.com/customer-success-registry/worker:latest

# Connect registry to cluster
doctl kubernetes cluster registry add customer-success-prod
```

## Step 4: Update Kubernetes Manifests

Update the image references in the deployment files:

```bash
# Update the API deployment
kubectl patch deployment customer-success-api -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","image":"registry.digitalocean.com/customer-success-registry/api:latest"}]}}}}'
```

Or update the YAML files directly:

```yaml
# infrastructure/kubernetes/deployments/api.yaml
spec:
  containers:
  - name: api
    image: registry.digitalocean.com/customer-success-registry/api:latest
    imagePullPolicy: Always
```

```yaml
# infrastructure/kubernetes/deployments/agent-workers.yaml
spec:
  containers:
  - name: message-processor
    image: registry.digitalocean.com/customer-success-registry/worker:latest
    imagePullPolicy: Always
```

## Step 5: Create Required Secrets

```bash
# OpenAI API Key
kubectl create secret generic api-keys \
  --from-literal=openai-api-key='sk-proj-your-actual-key-here' \
  --from-literal=twilio-account-sid='ACxxxxxxxxxxxx' \
  --from-literal=twilio-auth-token='your-auth-token'

# Database Credentials (use strong password!)
kubectl create secret generic database-credentials \
  --from-literal=database-url='postgresql+asyncpg://postgres:YOUR_STRONG_PASSWORD_HERE@postgresql-service:5432/customer_success' \
  --from-literal=username='postgres' \
  --from-literal=password='YOUR_STRONG_PASSWORD_HERE'

# Gmail Service Account (if using Gmail integration)
kubectl create secret generic gmail-credentials \
  --from-file=gmail-service-account.json=/path/to/your/gmail-service-account.json
```

## Step 6: Deploy Infrastructure Components

```bash
# Deploy PostgreSQL
kubectl apply -f infrastructure/kubernetes/deployments/postgresql.yaml
kubectl apply -f infrastructure/kubernetes/services/postgresql-service.yaml
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s

# Deploy Kafka
kubectl apply -f infrastructure/kubernetes/deployments/kafka.yaml
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s

# Create Kafka topics (run once)
kubectl exec -it kafka-0 -- /bin/bash -c '
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.tickets.incoming --partitions 12 --replication-factor 3
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.email.inbound --partitions 6 --replication-factor 3
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.whatsapp.inbound --partitions 6 --replication-factor 3
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.channels.webform.inbound --partitions 6 --replication-factor 3
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.escalations --partitions 3 --replication-factor 3
  kafka-topics.sh --bootstrap-server localhost:9092 --create --topic fte.dlq --partitions 3 --replication-factor 3
'
```

## Step 7: Deploy Application

```bash
# Deploy ConfigMap
kubectl apply -f infrastructure/kubernetes/configmaps/app-config.yaml

# Deploy API
kubectl apply -f infrastructure/kubernetes/deployments/api.yaml
kubectl apply -f infrastructure/kubernetes/services/api-service.yaml
kubectl wait --for=condition=ready pod -l app=customer-success-fte,component=api --timeout=300s

# Deploy Workers
kubectl apply -f infrastructure/kubernetes/deployments/agent-workers.yaml
kubectl wait --for=condition=ready pod -l app=customer-success-fte,component=agent-workers --timeout=300s
```

## Step 8: Install KEDA for Autoscaling

```bash
# Install KEDA
kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml

# Wait for KEDA
kubectl wait --for=condition=ready pod -l app=keda-operator -n keda --timeout=300s

# Apply ScaledObject for Kafka-based scaling
kubectl apply -f infrastructure/kubernetes/hpa/keda-scaledobject.yaml
```

## Step 9: Get Public URL

```bash
# Get LoadBalancer IP (may take 2-3 minutes)
kubectl get svc customer-success-api-service -w

# Once EXTERNAL-IP shows (e.g., 143.198.123.45):
export BACKEND_API_URL=$(kubectl get svc customer-success-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Backend API URL: http://$BACKEND_API_URL"

# Test
curl http://$BACKEND_API_URL/health
```

## Step 10: Set Up Domain (Optional but Recommended)

```bash
# 1. Point your domain to the LoadBalancer IP
# Add an A record in your DNS:
# api.yourdomain.com -> 143.198.123.45

# 2. Install cert-manager for TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 3. Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# 4. Update Ingress to use TLS
# Edit infrastructure/kubernetes/services/api-service.yaml to add:
# metadata:
#   annotations:
#     cert-manager.io/cluster-issuer: "letsencrypt-prod"
# spec:
#   tls:
#   - hosts:
#     - api.yourdomain.com
#     secretName: api-tls-cert
```

## Step 11: Configure Webhooks

Now that you have a public URL, configure webhooks:

#### Twilio WhatsApp Webhook

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
3. Set "When a message comes in" to:
   ```
   https://api.yourdomain.com/webhooks/twilio/whatsapp
   ```
   Or if no domain:
   ```
   http://143.198.123.45/webhooks/twilio/whatsapp
   ```

#### Gmail Pub/Sub Push

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Pub/Sub** → **Topics** → `gmail-notifications`
3. Create a subscription:
   - Name: `gmail-push-subscription`
   - Delivery type: **Push**
   - Endpoint URL: `https://api.yourdomain.com/webhooks/gmail`
4. Set up Gmail watch (run this with Gmail API credentials)

## Step 12: Monitor Deployment

```bash
# Check all pods
kubectl get pods

# Check metrics
curl http://$BACKEND_API_URL/metrics

# View logs
kubectl logs -l app=customer-success-fte,component=api --tail=100 -f
kubectl logs -l app=customer-success-fte,component=agent-workers --tail=100 -f

# Check autoscaling
kubectl get hpa
kubectl get scaledobject
```

## Step 13: Seed Knowledge Base

```bash
# Port-forward to PostgreSQL
kubectl port-forward svc/postgresql-service 5432:5432 &

# Run seeding script
cd scripts
python seed_knowledge_base.py

# Stop port-forward
kill %1
```

## Production Hardening Checklist

- [ ] Use strong database passwords (generated with `openssl rand -base64 32`)
- [ ] Enable TLS/HTTPS with cert-manager and Let's Encrypt
- [ ] Set up monitoring with Prometheus and Grafana
- [ ] Configure log aggregation (DigitalOcean Kubernetes logs)
- [ ] Enable network policies for pod-to-pod security
- [ ] Set resource limits on all pods
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up alerts for critical metrics (API errors, Kafka lag)
- [ ] Implement rate limiting on public endpoints
- [ ] Review and restrict RBAC permissions
- [ ] Enable pod security policies
- [ ] Set up disaster recovery procedures