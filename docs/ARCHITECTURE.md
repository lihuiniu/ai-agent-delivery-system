
### ARCHITECTURE.md

# AI Agent System Architecture

## Overview Diagram
```mermaid
%%{init: {'theme': 'neutral', 'fontFamily': 'Arial', 'gantt': {'barHeight': 20}}}%%
flowchart TD
    subgraph Azure Cloud
        A[Web/Mobile Client] -->|HTTPS| B[Azure API Management]
        B -->|mTLS| C[Istio Ingress]
        C --> D[Agent Service Pods]
        
        subgraph AKS Cluster
            D --> E[Redis Cache]
            D --> F[Azure Service Bus]
            E -->|Persistence| G[(Azure Disk)]
            F --> H[Action Dispatcher]
        end
        
        H --> I[Backend Services]
        I --> J[(Azure Cosmos DB)]
    end

    classDef azure fill:#007FFF,color:white,stroke:#333
    classDef k8s fill:#326CE5,color:white,stroke:#333
    classDef data fill:#FF6600,stroke:#333
    class A,B,I azure
    class C,D,H k8s
    class E,F,G,J data
```

## Component Flow Details
## Component Sequence
- [Request Lifecycle](./flows/request_lifecycle.md)
```mermaid
sequenceDiagram
    autonumber
    Client->>APIM: HTTPS Request (JWT)
    APIM->>Istio: Validate Token
    Istio->>AgentService: Forward
    AgentService->>Redis: Get State
    Redis-->>AgentService: Return Data
    AgentService->>OpenAI: API Call
    OpenAI-->>AgentService: Stream Response
    AgentService-->>Client: Return Tokens
```

## Data Relationships
- [Data Relationships](./flows/data_relationships.md)
```mermaid
erDiagram
    USER ||--o{ CONVERSATION : "has"
    CONVERSATION {
        string id PK
        timestamp created_at
    }
    CONVERSATION ||--|{ MESSAGE : "contains"
    MESSAGE {
        string id PK
        string content
    }
    AGENT_CONFIG ||--o{ CONVERSATION : "uses"
    AGENT_CONFIG {
        string id PK
        string model_type
    }
```

## Network Topology
```mermaid
graph LR
    Internet --> APIM
    APIM --> Istio
    Istio --> AgentService
    AgentService --> Redis
    AgentService --> ServiceBus
    ServiceBus --> Backend
    Backend --> CosmosDB
    
    subgraph Azure
        APIM
        Istio
        CosmosDB
    end
    
    subgraph AKS
        AgentService
        Redis
        ServiceBus
    end
```

## Key Metrics
```mermaid
pie
    title Resource Allocation
    "Compute" : 45
    "Memory" : 30
    "Storage" : 15
    "Network" : 10
```

## Key Decisions

1. **Streaming Architecture**:
   - FastAPI for native streaming support
   - AKS with HPA for scaling streaming connections
   - Redis for conversation state management

2. **Action Processing**:
   - Decoupled via Service Bus
   - Separate consumer service for reliability
   - Dead-letter queue for failed actions

3. **Evaluation Strategy**:
   - Offline: Pre-deployment with test cases
   - Online: Real-user interaction metrics
   - Versioned configurations for bisecting issues