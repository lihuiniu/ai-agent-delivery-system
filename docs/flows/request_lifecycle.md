# Request Lifecycle

## Full Sequence Diagram
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant APIM
    participant AgentService
    participant Redis
    participant OpenAI
    participant ServiceBus
    participant ActionDispatcher
    participant BackendServices
    participant MetricsDB

    User->>Frontend: Sends message
    Frontend->>APIM: POST /chat (with AAD token)
    APIM->>AgentService: Forward request
    AgentService->>Redis: Get config/history
    AgentService->>OpenAI: Stream request
    OpenAI-->>AgentService: Stream tokens
    AgentService-->>APIM: Stream response
    APIM-->>Frontend: Stream tokens
    Frontend-->>User: Display tokens

    alt Action Required
        AgentService->>ServiceBus: Publish action
        ServiceBus->>ActionDispatcher: Consume
        ActionDispatcher->>BackendServices: Execute
        BackendServices-->>ActionDispatcher: Result
        ActionDispatcher->>MetricsDB: Record
        ActionDispatcher-->>AgentService: Feedback (optional)
    end

    AgentService->>Redis: Update history
    AgentService->>MetricsDB: Record eval metrics
```

## Key Phases

1. **Authentication & Routing**
   - Azure AD validates JWT
   - API Gateway routes to appropriate agent

2. **Context Assembly**
   - Retrieves:
     - Agent config (from Blob Storage)
     - Conversation history (from Redis)

3. **LLM Processing**
   - Streaming call to OpenAI
   - Real-time token processing

4. **Action Handling** (Conditional)
   ```mermaid
   flowchart LR
       A[Action Detected] --> B[Service Bus]
       B --> C[Dispatcher]
       C --> D[Backend API]
   ```

5. **Persistence**
   - Conversation history updated
   - Evaluation metrics recorded

## Error Handling Paths
```mermaid
graph TD
    A[Request Start] --> B{Valid?}
    B -->|Yes| C[Process]
    B -->|No| D[401 Error]
    C --> E{LLM Error?}
    E -->|Yes| F[Fallback Model]
    E -->|No| G[Complete]
```