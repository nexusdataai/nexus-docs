# Developer Guide

This section provides development guides, API documentation, testing procedures, and setup instructions for developers working on the NexusAI platform.

## Overview

The developer documentation includes:

- **Getting Started** - Development environment setup
- **Backend Development** - Backend service development
- **Frontend Development** - UI application development
- **API Documentation** - REST APIs and MCP tools
- **Testing** - Unit, integration, and E2E testing
- **LocalStack** - Local development environment

## Available Documents

### Backend Development

#### Backend README
Comprehensive guide to the backend service architecture, setup, and development.

📄 [View Backend README](backend/README.md)

---

#### LocalStack Setup
Guide to setting up LocalStack for local development without AWS costs.

📄 [View LocalStack Setup Guide](backend/env-local-example.md)

---

### Additional Resources

#### Requirements Documentation
📄 [View Requirements](requirements/)

#### MCP Tools Documentation
📄 [View MCP Tools](mcp-tools/)

#### LocalStack Documentation
📄 [View LocalStack Docs](localstack/)

#### Claude Integration
📄 [View Claude Integration](claude/)

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18+ (for frontend)
- **Docker**: Latest version
- **Git**: Latest version
- **AWS CLI**: Latest version (optional)

### Backend Setup

#### Option 1: LocalStack (Recommended for Development)

```bash
# Clone repository
git clone <repository-url>
cd nexus-backend

# Start LocalStack
docker-compose -f docker-compose-localstack.yml up -d

# Setup environment
cp .env.localstack.example .env.local
export USE_LOCALSTACK=true
export LOCALSTACK_HOST=localhost
export LOCALSTACK_PORT=4566

# Install dependencies
pip install -r requirements.txt

# Initialize LocalStack resources
python -m tests.localstack_automation.run_automation --setup

# Start gateway
./gateway.sh start

# Verify
./gateway.sh test
```

#### Option 2: Real AWS

```bash
# Configure AWS credentials
aws configure
# or
export AWS_PROFILE=your-profile

# Setup environment
export ENVIRONMENT=dev
export AWS_REGION=ap-southeast-1

# Install dependencies
pip install -r requirements.txt

# Start gateway
./gateway.sh start
```

### Frontend Setup

```bash
# Clone repository
git clone <repository-url>
cd nexus-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Implement Changes

- Write code following project conventions
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Backend tests
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/bdd/ -v

# Frontend tests
npm test
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Testing

### Backend Testing

#### Unit Tests
Test individual components in isolation:

```bash
pytest tests/unit/ -v
```

#### Integration Tests
Test component interactions with LocalStack:

```bash
USE_LOCALSTACK=true pytest tests/integration/ -v
```

#### BDD Tests
Behavior-driven development tests:

```bash
pytest tests/bdd/ -v --gherkin-terminal-reporter
```

#### E2E Tests
End-to-end testing:

```bash
pytest tests/e2e/ -v
```

### Frontend Testing

#### Unit Tests
```bash
npm run test:unit
```

#### Component Tests
```bash
npm run test:component
```

#### E2E Tests
```bash
npm run test:e2e
```

## API Development

### REST APIs

The platform exposes REST APIs via FastAPI:

```python
from fastapi import APIRouter, Depends
from src.models import Journey

router = APIRouter()

@router.post("/api/v1/journeys")
async def create_journey(journey: Journey):
    # Implementation
    pass
```

### MCP Tools

MCP tools for AI agent integration:

```python
from src.tools.base_tool import MCPTool

class MyTool(MCPTool):
    def execute(self, params):
        # Implementation
        pass
```

## Code Standards

### Python Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Max line length: 100 characters

```python
from typing import List, Optional

def process_call(
    call_id: str,
    options: Optional[dict] = None
) -> dict:
    """
    Process a single call.
    
    Args:
        call_id: The call identifier
        options: Optional processing options
        
    Returns:
        Processing result dictionary
    """
    pass
```

### TypeScript Code Style

- Use TypeScript strict mode
- Follow ESLint rules
- Use functional components
- Implement proper typing

```typescript
interface CallData {
  id: string;
  timestamp: number;
  duration: number;
}

const ProcessCall: React.FC<{ call: CallData }> = ({ call }) => {
  // Implementation
};
```

## Debugging

### Backend Debugging

#### Using Python Debugger
```python
import pdb; pdb.set_trace()
```

#### VSCode Debugging
```json
{
  "type": "python",
  "request": "launch",
  "name": "Gateway",
  "program": "${workspaceFolder}/mcp_http_gateway.py",
  "console": "integratedTerminal"
}
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("Debug message")
```

### Frontend Debugging

#### Browser DevTools
- Use React Developer Tools
- Check Network tab for API calls
- Use Console for logs

#### VSCode Debugging
```json
{
  "type": "chrome",
  "request": "launch",
  "name": "Launch Chrome",
  "url": "http://localhost:3000",
  "webRoot": "${workspaceFolder}/src"
}
```

## Common Development Tasks

### Add a New API Endpoint

1. Create endpoint in `src/apis/`
2. Add route to gateway
3. Write tests
4. Update API documentation

### Add a New MCP Tool

1. Create tool class in `src/tools/`
2. Implement execute method
3. Register tool in gateway
4. Write tests
5. Update tool documentation

### Add a New Transformation Stage

1. Create stage class in `src/stages/`
2. Inherit from `BaseStage`
3. Implement process method
4. Add stage configuration
5. Write tests

### Update Database Schema

1. Modify table definition
2. Create migration script
3. Update models
4. Test with LocalStack
5. Document changes

## Performance Optimization

### Backend Optimization

- Use async/await for I/O operations
- Implement caching where appropriate
- Optimize database queries
- Use batch operations
- Profile with `cProfile`

### Frontend Optimization

- Code splitting
- Lazy loading
- Memoization
- Virtual scrolling
- Bundle optimization

## Security Best Practices

### Backend Security

- Validate all inputs
- Use parameterized queries
- Store secrets securely
- Implement rate limiting
- Use HTTPS only

### Frontend Security

- Sanitize user inputs
- Implement CSRF protection
- Use Content Security Policy
- Secure authentication tokens
- Regular dependency updates

## Documentation

### Code Documentation

- Write clear docstrings
- Add inline comments for complex logic
- Update README files
- Document API changes

### API Documentation

- Use OpenAPI/Swagger
- Provide examples
- Document error responses
- Keep documentation in sync with code

## Resources

### Internal Documentation
- [Architecture](../technical/architecture/job-execution-flow.md)
- [Call Processing](../technical/nexus-ai/)
- [Gateway](../technical/gateway/)
- [Database Design](../technical/dbdesign/journey-data.md)

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [AWS SDK for Python](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [LocalStack Documentation](https://docs.localstack.cloud/)

---

## Getting Help

- 📖 Check existing documentation
- 🔍 Search codebase for examples
- 💬 Ask in team chat
- 🐛 Check issue tracker
- 📝 Create detailed bug reports

---

[← Back to Home](../index.md) | [← Previous: Operational Documentation](../operational/)
