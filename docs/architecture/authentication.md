# Authentication Workflow

## End-to-End Sequence
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client
    participant AAD as "Azure AD"
    participant APIG as "API Gateway"
    participant Agent
    participant Backend

    User->>Client: Initiates request
    Client->>AAD: 1. Request token (client credentials)
    AAD-->>Client: 2. Returns JWT (expires_in: 3600s)
    Client->>APIG: 3. API call (Authorization: Bearer {JWT})
    APIG->>AAD: 4. Validate token (/.well-known/openid-configuration)
    AAD-->>APIG: 5. Validation response (sub, aud, scopes)
    
    alt Valid token
        APIG->>Agent: 6. Forward request (X-User-Id:{sub})
        Agent->>Backend: 7. Authorized action (X-User-Id)
        Backend-->>Agent: 8. Action result (200 OK)
        Agent-->>APIG: 9. Response
        APIG-->>Client: 10. Return data
        Client-->>User: Display result
    else Invalid token
        APIG-->>Client: 401 Unauthorized (WWW-Authenticate: Bearer)
        Client-->>User: Show error
    end
```

## Key Components

### 1. Token Acquisition
```mermaid
flowchart LR
    A[Client] -->|Client ID + Secret| B(Azure AD)
    B -->|JWT| C[Contains:\nsub\nemail\nscopes\nexp]
```

### 2. Claim Propagation
```mermaid
journey
    title Claim Flow Through Services
    section API Gateway
      Extract sub: 3
      Validate scopes: 3
    section Agent Service
      Attach to logs: 2
      Enforce permissions: 4
    section Backend
      Personalize response: 1
```

## Implementation Details

### Required Headers
| Header | Example | Description |
|--------|---------|-------------|
| `Authorization` | `Bearer eyJhbGci...` | Must include valid JWT |
| `X-User-Id` | `7a34b8c1` | Propagated user context |
| `X-Action-Scope` | `notifications:write` | Required permissions |

### Token Validation Logic
```python
# Pseudocode for API Gateway validation
def validate_token(token):
    jwks_uri = get_jwks_uri()  # From Azure AD discovery endpoint
    public_key = fetch_public_key(jwks_uri, token.header['kid'])
    
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        audience='api://your-app-id',
        issuer='https://login.microsoftonline.com/tenant-id/v2.0'
    )
    
    verify_scope(decoded, required='api.access')
    return decoded['sub']  # Return user identifier
```

## Error Handling

```mermaid
stateDiagram-v2
    [*] --> Valid
    Valid --> InvalidToken: Expired/Invalid
    Valid --> InsufficientScope: Missing permissions
    InvalidToken --> [*]: 401 Unauthorized
    InsufficientScope --> [*]: 403 Forbidden
```

## Performance Benchmarks
| Operation | 50th % (ms) | 99th % (ms) |
|-----------|-------------|-------------|
| Token Acquisition | 120 | 350 |
| Gateway Validation | 15 | 45 |
| Permission Check | 5 | 12 |

## Security Controls
1. **JWT Requirements**:
   - RS256 signing
   - 1-hour expiration
   - `aud` claim matching API identifier
2. **Rate Limiting**:
   - 100 token requests/minute/client
3. **Revocation**:
   - Azure AD token revocation endpoint
   - Local cache invalidation

```mermaid
pie
    title Security Features
    "Token Validation" : 35
    "Rate Limiting" : 25
    "Audit Logging" : 20
    "Encryption" : 20
```

## Example Curl Request
```bash
# Get token
curl -X POST "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id={id}&scope=api://your-app-id/.default&client_secret={secret}&grant_type=client_credentials"

# Call API
curl -X GET "https://api.example.com/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: 1234"
```

## Related Documents
- [Azure AD Integration Guide](./azure_ad_setup.md)
- [Token Best Practices](./security/token_management.md)
- [Audit Logging Spec](./logging/authentication_audits.md)