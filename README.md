# AI Agent Delivery System

This project provides a complete solution for delivering AI agents within an existing application on Azure.

## Features

- Token-by-token streamed chat responses
- Configurable agent system with versioning
- Authenticated action execution
- Comprehensive evaluation system (offline/online)
- CI/CD pipelines with canary deployment
- Observability and monitoring

## Prerequisites

- Azure subscription
- Terraform v1.0+
- kubectl
- helm
- Python 3.9+

## Quick Start

1. Set up infrastructure:
```bash
cd infrastructure
terraform init
terraform apply


2. Deploy the agent service:
```bash
helm install agent-service ./charts/agent-service

3. Run the FastAPI application:
```bash
cd ../agent-service
pip install -r requirements.txt
uvicorn main:app --reload

## Documentation

### [Architecture Overview](docs/ARCHITECTURE.md)
High-level system design and component interactions.  
![Architecture Diagram](docs/images/architecture.png)

### [User Flow](docs/USER_FLOW.md)
Step-by-step interaction patterns and system workflows.  
![User Flow Chart](docs/images/user-flow.png)

### Infrastructure Guides
- [Terraform Setup](infrastructure/README.md) - Cloud provisioning instructions
- [Kubernetes Deployment](charts/README.md) - Helm chart configurations

### Agent Configuration
- [Configuration Management](docs/agent-configuration.md) - Versioning and deployment
- [Evaluation Framework](docs/evaluation.md) - Offline/online testing procedures

### Decision Records
- [ADR-001: Configuration Versioning](docs/adr/001-agent-configuration.md)

