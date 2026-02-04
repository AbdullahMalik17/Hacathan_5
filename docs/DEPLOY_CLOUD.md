# Cloud Platform Deployment Guide

Complete guide for deploying Customer Success Digital FTE to production Kubernetes platforms (GKE, EKS, AKS, DigitalOcean).

## Cloud Platform Options

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Google GKE** | Autopilot mode, excellent networking, native Pub/Sub | Higher cost | Gmail integration, Google Workspace |
| **AWS EKS** | Broad service ecosystem, IAM integration | Complex setup | Enterprise, AWS-native apps |
| **Azure AKS** | Cost-effective, good for enterprises | Learning curve | Microsoft shops |
| **DigitalOcean DOKS** | Simple, affordable ($12/mo), fast setup | Fewer features | Startups, MVPs |

**Recommendation for this project:** DigitalOcean Kubernetes (DOKS) for simplicity and cost-effectiveness.

---

## Option 1: DigitalOcean Kubernetes (Recommended)

### Prerequisites

1. **DigitalOcean Account**: Sign up at [digitalocean.com](https://www.digitalocean.com)
2. **doctl CLI**: Install command-line tool
   ```bash
   # macOS
   brew install doctl

   # Windows (Chocolatey)
   choco install doctl

   # Linux
   cd /tmp && wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
   tar xf doctl-1.104.0-linux-amd64.tar.gz && sudo mv doctl /usr/local/bin
   ```

3. **Authenticate doctl**:
   ```bash
   doctl auth init
   # Enter your DigitalOcean API token (create at cloud.digitalocean.com/account/api/tokens)
   ```

---

### Step 1: Create Kubernetes Cluster

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

### Step 2: Configure kubectl

```bash
# Download kubeconfig
doctl kubernetes cluster kubeconfig save customer-success-prod

# Verify connection
kubectl get nodes
```

### Step 3: Set Up Container Registry

```bash
# Create DigitalOcean Container Registry
doctl registry create customer-success-registry

# Authenticate Docker
doctl registry login

# Tag and push images
docker tag customer-success-api:latest registry.digitalocean.com/customer-success-registry/api:latest
docker tag customer-success-frontend:latest registry.digitalocean.com/customer-success-registry/frontend:latest

docker push registry.digitalocean.com/customer-success-registry/api:latest
docker push registry.digitalocean.com/customer-success-registry/frontend:latest

# Connect registry to cluster
doctl kubernetes cluster registry add customer-success-prod
```

### Step 4: Update Kubernetes Manifests

Update image references in deployment files:

```yaml
# infrastructure/kubernetes/deployments/api.yaml
spec:
  containers:
  - name: api
    image: registry.digitalocean.com/customer-success-registry/api:latest
    imagePullPolicy: Always
```

### Step 5: Create Secrets

```bash
# OpenAI API Key
kubectl create secret generic openai-api-key \
  --from-literal=OPENAI_API_KEY='sk-proj-your-actual-key-here'

# Twilio Credentials
kubectl create secret generic twilio-credentials \
  --from-literal=TWILIO_ACCOUNT_SID='ACxxxxxxxxxxxx' \
  --from-literal=TWILIO_AUTH_TOKEN='your-auth-token' \
  --from-literal=TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'

# Database Credentials (use strong password!)
kubectl create secret generic database-credentials \
  --from-literal=POSTGRES_USER='postgres' \
  --from-literal=POSTGRES_PASSWORD='$(openssl rand -base64 32)' \
  --from-literal=DATABASE_URL='postgresql+asyncpg://postgres:PASSWORD@postgresql-service:5432/customer_success'

# Gmail Service Account
kubectl create secret generic gmail-service-account \
  --from-file=gmail-service-account.json=backend/credentials/gmail-service-account.json
```

### Step 6: Deploy Application

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

# Deploy ConfigMap
kubectl apply -f infrastructure/kubernetes/configmaps/app-config.yaml

# Deploy API
kubectl apply -f infrastructure/kubernetes/deployments/api.yaml
kubectl apply -f infrastructure/kubernetes/services/api-service.yaml
kubectl wait --for=condition=ready pod -l app=customer-success-api --timeout=300s

# Deploy Workers
kubectl apply -f infrastructure/kubernetes/deployments/agent-workers.yaml
kubectl wait --for=condition=ready pod -l app=agent-workers --timeout=300s
```

### Step 7: Install KEDA for Autoscaling

```bash
# Install KEDA
kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml

# Wait for KEDA
kubectl wait --for=condition=ready pod -l app=keda-operator -n keda --timeout=300s

# Apply ScaledObject
kubectl apply -f infrastructure/kubernetes/hpa/keda-scaledobject.yaml
```

### Step 8: Get Public URL

```bash
# Get LoadBalancer IP (may take 2-3 minutes)
kubectl get svc api-service -w

# Once EXTERNAL-IP shows (e.g., 143.198.123.45):
export API_URL=$(kubectl get svc api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "API URL: http://$API_URL"

# Test
curl http://$API_URL/health
```

### Step 9: Set Up Domain (Optional but Recommended)

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

### Step 10: Configure Webhooks

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
4. Set up Gmail watch (run this with Gmail API credentials):
   ```bash
   # This requires Gmail API setup and authenticated credentials
   # See Gmail API documentation for watch setup
   ```

---

### Step 11: Monitor Deployment

```bash
# Check all pods
kubectl get pods

# Check metrics
curl http://$API_URL/metrics

# View logs
kubectl logs -l app=customer-success-api --tail=100 -f
kubectl logs -l app=agent-workers --tail=100 -f

# Check autoscaling
kubectl get hpa
kubectl get scaledobject
```

---

### Step 12: Seed Knowledge Base

```bash
# Port-forward to PostgreSQL
kubectl port-forward svc/postgresql-service 5432:5432 &

# Run seeding script
cd scripts
python seed_knowledge_base.py

# Stop port-forward
kill %1
```

---

### Production Hardening Checklist

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

---

## Option 2: Google Kubernetes Engine (GKE)

**Best for:** Gmail integration, Google Workspace environments

### Quick Start

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Create cluster with Autopilot (managed nodes)
gcloud container clusters create-auto customer-success-prod \
  --region=us-central1 \
  --project=your-project-id

# Get credentials
gcloud container clusters get-credentials customer-success-prod \
  --region=us-central1

# Follow steps 3-12 from DigitalOcean guide above
```

**Estimated Cost:** $80-150/month (Autopilot mode)

---

## Option 3: Amazon EKS

**Best for:** AWS-native environments, enterprise

### Quick Start

```bash
# Install eksctl
brew install eksctl  # macOS
# or: curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp && sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name customer-success-prod \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 6 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --name customer-success-prod --region us-east-1

# Follow steps 3-12 from DigitalOcean guide above
```

**Estimated Cost:** $75-120/month (EKS control plane + EC2 nodes)

---

## Option 4: Azure AKS

**Best for:** Microsoft-centric organizations

### Quick Start

```bash
# Install Azure CLI
curl -L https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name customer-success-rg --location eastus

# Create cluster
az aks create \
  --resource-group customer-success-rg \
  --name customer-success-prod \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group customer-success-rg --name customer-success-prod

# Follow steps 3-12 from DigitalOcean guide above
```

**Estimated Cost:** $70-130/month

---

## CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Build and push images
        run: |
          doctl registry login
          docker build -t registry.digitalocean.com/customer-success-registry/api:${{ github.sha }} ./backend
          docker build -t registry.digitalocean.com/customer-success-registry/frontend:${{ github.sha }} ./frontend
          docker push registry.digitalocean.com/customer-success-registry/api:${{ github.sha }}
          docker push registry.digitalocean.com/customer-success-registry/frontend:${{ github.sha }}

      - name: Update kubeconfig
        run: doctl kubernetes cluster kubeconfig save customer-success-prod

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/customer-success-api api=registry.digitalocean.com/customer-success-registry/api:${{ github.sha }}
          kubectl rollout status deployment/customer-success-api
```

---

## Monitoring Setup (Recommended)

### Install Prometheus and Grafana

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Login: admin / prom-operator (default password)
```

### Import Dashboards

1. Access Grafana at http://localhost:3000
2. Import dashboard ID **3662** (Prometheus 2.0 Overview)
3. Import dashboard ID **11074** (Node Exporter for Prometheus)
4. Create custom dashboard for application metrics from `/metrics` endpoint

---

## Cost Optimization Tips

1. **Use DigitalOcean** for the best price/performance ratio ($48-96/month)
2. **Enable cluster autoscaling** to scale down during low traffic
3. **Use spot instances** on AWS/GCP (50-70% cost savings)
4. **Right-size pods** - start with lower resource requests/limits
5. **Implement aggressive caching** to reduce OpenAI API calls
6. **Use reserved instances** for predictable workloads (30-40% savings)

---

## Troubleshooting

### Pods stuck in ImagePullBackOff

```bash
# Verify registry is connected
kubectl get pods -n kube-system | grep registry

# Reconnect registry (DigitalOcean)
doctl kubernetes cluster registry add customer-success-prod
```

### LoadBalancer stuck in Pending

```bash
# Check service
kubectl describe svc api-service

# Verify cloud provider LoadBalancer quota
# DigitalOcean: Check account limits in dashboard
```

### High costs

```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# Scale down non-production workloads
kubectl scale deployment customer-success-api --replicas=1
kubectl scale deployment agent-workers --replicas=1
```

---

**Deployment Complete!** 🎉

Your Customer Success Digital FTE is now running in production on a cloud Kubernetes platform.

Next steps:
1. Set up monitoring and alerts
2. Configure automated backups
3. Run load testing
4. Document runbooks for common operations
