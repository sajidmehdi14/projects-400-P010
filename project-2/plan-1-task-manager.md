# plan-1-task-manager.md
AI Native Task Manager — Kubernetes Deployment Plan
🧩 Architecture Overview

```mermaid
flowchart LR
    UI[UI Interface] -->|REST| BE[Backend APIs]
    UI -->|Direct| AG[Todo Agent]
    BE --> AG
    BE --> NS[Notification Service]
    NS --> UI
```

## Kubernetes Architecture
```mermaid
flowchart TB
    subgraph Namespace: task-manager-prod
        UI_POD[UI Pods x2]
        BE_POD[Backend Pods x3]
        AG_POD[Todo Agent Pods x2]
        NS_POD[Notification Pods x2]
    end

    UI_SVC[LoadBalancer] --> UI_POD
    BE_SVC[ClusterIP] --> BE_POD
    AG_SVC[ClusterIP] --> AG_POD
    NS_SVC[ClusterIP] --> NS_POD
```

## Deployments

| Component            | Type       | Replicas | Strategy      |
| -------------------- | ---------- | -------- | ------------- |
| UI                   | Deployment | 2        | Rolling       |
| Backend APIs         | Deployment | 3        | Rolling       |
| Todo Agent           | Deployment | 2        | Rolling       |
| Notification Service | Deployment | 2        | Rolling       |

## Services

| Service      | Type         | Exposure |
| ------------ | ------------ | -------- |
| UI           | LoadBalancer | Public   |
| Backend      | ClusterIP    | Internal |
| Todo Agent   | ClusterIP    | Internal |
| Notification | ClusterIP    | Internal |


## ConfigMaps
```yaml
ui-config:
  API_BASE_URL: /api

backend-config:
  DB_HOST: postgres
  FEATURE_FLAG: true

agent-config:
  MODEL: gpt
  TIMEOUT: 30

notification-config:
  QUEUE: redis
```

## Secrets
db-credentials  
api-keys  
notification-tokens  

## Best Practice

Use External Secrets Operator (Vault)  
Enable rotation

## RBAC

```mermaid
flowchart LR
    SA[Service Account] --> Role
    Role --> Resources[Pods/Services/ConfigMaps]

```

## 🔄 Inter-Service Communication

| Source  | Target       | Protocol    |
| ------- | ------------ | ----------- |
| UI      | Backend      | REST        |
| UI      | Agent        | HTTP        |
| Backend | Agent        | gRPC        |
| Backend | Notification | Queue/Event |

## Scaling

```mermaid
flowchart LR
    Metrics --> HPA
    HPA --> Pods
```

HPA enabled
CPU + Request-based scaling


## Observability
Logging: Fluentd
Monitoring: Prometheus
Dashboard: Grafana


## Security
TLS everywhere
NetworkPolicies (restrict pod communication)
Image scanning (CI/CD)