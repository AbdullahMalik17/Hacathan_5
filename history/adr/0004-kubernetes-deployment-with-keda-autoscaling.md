# ADR-0004: Kubernetes Deployment with KEDA Autoscaling

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-31
- **Feature:** 001-customer-success-fte
- **Context:** System requires 24/7 availability (99.5% uptime), dynamic scaling to handle traffic spikes (1000 concurrent conversations), and cost efficiency (<$2,000/year total). Constitution Principle VIII (Deployment-Ready Infrastructure) mandates container orchestration with autoscaling. Agent workers must scale based on Kafka consumer lag, not just CPU/memory.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Production operations and reliability
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Docker Compose, serverless, VMs, ECS
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all services and operational characteristics
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **Kubernetes** with the following deployment architecture:

- **Orchestration Platform**: Kubernetes (Minikube local, AKS/GKE/DOKS production)
- **Autoscaling**: KEDA (Kubernetes Event-Driven Autoscaling) for Kafka lag-based scaling
- **Deployment Types**:
  - Deployment: api (FastAPI webhook server, 3 replicas)
  - Deployment: agent-workers (Kafka consumers, 2-12 replicas with KEDA)
  - StatefulSet: postgresql (pgvector enabled, single replica with PVC)
  - StatefulSet: kafka (3 brokers with persistent volumes)
- **Service Mesh**: None (start simple with standard Kubernetes Services)
- **Configuration Management**: ConfigMaps for non-sensitive config, Secrets for API keys/credentials
- **Health Checks**: Liveness probe on /health, Readiness probe on /ready (checks DB + Kafka connectivity)
- **Graceful Shutdown**: preStop hooks with 30s sleep + 60s terminationGracePeriodSeconds

**KEDA Autoscaling Configuration**:
```yaml
triggers:
- type: kafka
  metadata:
    topic: fte.tickets.incoming
    lagThreshold: "100"        # Scale up when lag >100 messages
    bootstrapServers: kafka:9092
    consumerGroup: agent-workers
minReplicaCount: 2             # Always running for high availability
maxReplicaCount: 12            # Matches partition count for max parallelism
cooldownPeriod: 300            # 5 min cooldown to prevent thrashing
```

**Resource Allocation**:
```yaml
api:
  requests: {cpu: 500m, memory: 512Mi}
  limits: {cpu: 1000m, memory: 1Gi}
agent-workers:
  requests: {cpu: 1000m, memory: 1Gi}
  limits: {cpu: 2000m, memory: 2Gi}
postgresql:
  requests: {cpu: 1000m, memory: 2Gi}
  limits: {cpu: 2000m, memory: 4Gi}
```

## Consequences

### Positive

- **Event-Driven Autoscaling**: KEDA scales workers based on Kafka lag (actual work backlog) not CPU/memory, preventing under/over-provisioning
- **High Availability**: Multiple replicas with rolling updates ensure zero-downtime deployments
- **Resource Efficiency**: Workers scale down to 2 replicas during low traffic (nights/weekends) saving ~60% compute costs
- **Declarative Infrastructure**: Kubernetes manifests in Git provide version control and GitOps workflows
- **Multi-Cloud Portability**: Same manifests work on Minikube (local), AKS (Azure), GKE (Google), DOKS (DigitalOcean)
- **Self-Healing**: Kubernetes restarts failed pods automatically, ensures uptime SLA
- **Graceful Shutdown**: preStop hooks allow agent workers to finish processing current message before termination
- **Constitution Alignment**: Directly mandated by Principle VIII (Deployment-Ready Infrastructure)

### Negative

- **Learning Curve**: Team must learn Kubernetes concepts (pods, services, ingress, volumes, RBAC)
- **Local Complexity**: Minikube requires 4GB RAM minimum, slower developer onboarding vs Docker Compose
- **Operational Overhead**: Production requires monitoring (Prometheus), log aggregation (Loki), alerting setup
- **Overkill for MVP**: Kubernetes complexity unnecessary for initial development (Docker Compose simpler for local testing)
- **StatefulSet Limitations**: Single PostgreSQL replica means database is single point of failure (HA requires operator like CloudNativePG)
- **KEDA Dependency**: Additional component to manage and version (KEDA v2.12+ required for Kafka trigger improvements)

## Alternatives Considered

### Alternative A: Docker Compose for Production
- **Stack**: Docker Compose + VM-based deployment + Manual scaling
- **Why Rejected**:
  - No autoscaling (manual intervention required for traffic spikes)
  - No self-healing (failed containers require manual restart)
  - Single-host deployment (VM failure causes full outage)
  - Scaling requires manual docker-compose up --scale, no event-driven triggers
  - Constitution mandates Kubernetes (Principle VIII)

### Alternative B: Serverless (AWS Lambda + SQS)
- **Stack**: Lambda functions for webhooks + workers + SQS for queuing + RDS for PostgreSQL
- **Why Rejected**:
  - Cold start latency (100-500ms) violates <3s agent response requirement
  - Lambda 15-minute timeout too short for long-running agent processing
  - Vendor lock-in to AWS prevents multi-cloud deployment
  - Higher cost at scale (~$1,500/year for 10M invocations vs Kubernetes ~$500/year)
  - pgvector extension not available on RDS (requires self-hosted PostgreSQL anyway)
  - Constitution requires self-hosted Kubernetes

### Alternative C: Amazon ECS with Fargate
- **Stack**: ECS for orchestration + Fargate for serverless containers + ALB for load balancing
- **Why Rejected**:
  - Vendor lock-in to AWS (no multi-cloud portability)
  - Fargate pricing $36/month per vCPU + $4/month per GB RAM (~$900/year vs Kubernetes ~$500/year)
  - ECS autoscaling less flexible than KEDA (no built-in Kafka lag triggers)
  - Weaker ecosystem for tools and extensions compared to Kubernetes
  - Constitution mandates Kubernetes specifically

### Alternative D: Nomad with Consul
- **Stack**: HashiCorp Nomad for orchestration + Consul for service discovery + Custom autoscaling
- **Why Rejected**:
  - Smaller ecosystem and community compared to Kubernetes
  - No equivalent to KEDA for event-driven autoscaling (must build custom)
  - Less mature managed services (no equivalent to GKE, AKS, EKS)
  - Team lacks Nomad expertise
  - Constitution requires Kubernetes

## References

- Feature Spec: specs/001-customer-success-fte/spec.md (NFR-004: 1000 concurrent conversations, NFR-006: 99.5% uptime)
- Implementation Plan: specs/001-customer-success-fte/plan.md (Phase 0: Research - Section 6, Path 4: Deployment Infrastructure)
- Research Document: specs/001-customer-success-fte/research.md (Section 6: Kubernetes Deployment)
- Tasks: specs/001-customer-success-fte/tasks.md (Phase 8: Deployment Infrastructure tasks T092-T103)
- Related ADRs: ADR-0003 (Event-Driven Architecture) for KEDA scaling triggers on Kafka lag
- Constitution: .specify/memory/constitution.md (Principle VIII: Deployment-Ready Infrastructure)
