# Development Guide

## Project Overview

**DDN AI Test Failure Analysis System** is an intelligent AI-powered system for analyzing test failures, generating insights, and automating test execution through LangGraph-based orchestration.

### Key Components

1. **LangGraph ReAct Agent** (7-node workflow)
   - Route incoming failures
   - Analyze test data and logs
   - Generate insights
   - Recommend fixes

2. **Dual-Index RAG System** (80/20 reasoning/synthesis split)
   - Pinecone vector database
   - Semantic search
   - Context routing

3. **Multi-LLM Support** (Claude, Gemini, OpenAI)
   - Automatic fallback
   - Model-specific optimizations

4. **Dashboard** (React/TypeScript)
   - Real-time monitoring
   - Failure visualization
   - Workflow triggering

## Architecture

### Directory Structure

```
ddn-ai-test-analysis/
├── implementation/           # Core system code
│   ├── agents/              # LangGraph agents
│   ├── services/            # Microservices
│   ├── models/              # Data models
│   ├── utils/               # Utilities
│   └── evaluation/          # Testing & evaluation
├── dashboard/               # Frontend (React)
├── scripts/                 # Helper scripts
├── docs/                    # Documentation
├── docker-compose.yml       # Service orchestration
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

### Technology Stack

**Backend**:
- Python 3.9+
- LangGraph (agent orchestration)
- FastAPI (REST API)
- SQLAlchemy (ORM)
- Celery (async tasks)

**Frontend**:
- React 18+
- TypeScript
- Vite (build tool)
- TailwindCSS (styling)

**Data**:
- PostgreSQL (primary database)
- MongoDB Atlas (failure logs)
- Redis (cache & queue)
- Pinecone (vector database)

**Infrastructure**:
- Docker & Docker Compose
- Jenkins (CI/CD)
- n8n (workflow automation)
- Langfuse (LLM monitoring)

## Getting Started

### 1. Prerequisites

```bash
# Check Python version
python --version  # 3.9 or higher

# Check Docker
docker --version
docker-compose --version
```

### 2. Environment Setup

```bash
# Clone repository
git clone https://github.com/Sushrut-01/ddn-ai-test-analysis.git
cd ddn-ai-test-analysis

# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# Create .env from template
cp .env.example .env

# Edit .env with your credentials
# At minimum, set:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - POSTGRES_PASSWORD
# - MONGODB_ATLAS_URI
# - PINECONE_API_KEY
```

### 3. Start Services

```bash
# Start all Docker services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f  # All services
docker-compose logs -f langfuse  # Specific service
```

### 4. Initialize Database

```bash
cd implementation
python create_database.py  # Create tables
python seed_database.py    # Load sample data
```

## Development Workflow

### Running the Application

```bash
# Terminal 1: Start API server
cd implementation
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Terminal 2: Start Celery worker
celery -A agents.celery_app worker --loglevel=info

# Terminal 3: Start dashboard
cd dashboard
npm run dev

# Terminal 4: Start RAG service
cd implementation
python services/rag_service.py
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py::test_analyze_failure -v

# With coverage
pytest tests/ --cov=implementation --cov-report=html

# Integration tests
pytest tests/integration/ -v
```

### Debugging

```bash
# Add breakpoints in code
import pdb; pdb.set_trace()

# Run with debugger
python -m pdb implementation/main.py

# VS Code debugging
# Use .vscode/launch.json configuration
```

## Core Concepts

### LangGraph Agent Flow

```
Input Test Failure
        ↓
    Route Node
   /    |    \
  /     |     \
Analyze Log Analysis Context RAG
  \     |     /
   \    |    /
  Reasoning Node
        ↓
  Synthesis Node
        ↓
   Generate Output
```

### RAG Routing Logic

- **80% Reasoning**: Use chain-of-thought, SQL analysis, error pattern matching
- **20% Synthesis**: Use context from vector database for similar failures
- **CRAG**: Corrective generation if confidence < 0.7

### Service Dependencies

```
API (5000)
    ├── PostgreSQL (5432)
    ├── Redis (6379)
    └── RAG Service (5006)
        ├── Pinecone (API)
        └── LLM APIs

Dashboard (5173)
    ├── API (5000)
    ├── Langfuse (3000)
    └── Jenkins (8080)
```

## Common Tasks

### Adding a New LLM Provider

1. Create provider module in `implementation/services/llm_providers/`
2. Implement `BaseLLMProvider` interface
3. Add configuration in `.env.example`
4. Update `services/llm_manager.py` to load provider
5. Test with existing workflows

### Creating New Endpoints

1. Create route handler in `implementation/api/routes/`
2. Define request/response models in `models/schemas/`
3. Add tests in `tests/test_api/`
4. Update API documentation
5. Trigger tests with: `pytest tests/test_api/test_new_route.py`

### Modifying Database Schema

1. Create migration file:
   ```bash
   alembic revision --autogenerate -m "Add new field"
   ```
2. Review and edit migration in `implementation/alembic/versions/`
3. Apply migration:
   ```bash
   alembic upgrade head
   ```
4. Update models in `implementation/models/`

### Updating Documentation

- Update `.md` files in `docs/` and root
- Include examples and code snippets
- Update diagrams if architecture changes
- Run documentation checks

## Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Docker service won't start

```bash
# Check logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>

# Clean and rebuild
docker-compose down -v
docker-compose up -d
```

### LLM API errors

- Verify API keys in `.env`
- Check API rate limits
- Review error logs: `docker-compose logs langfuse`

### Database connection errors

```bash
# Check PostgreSQL connection
psql -h localhost -U ddn_user -d ddn_ai_db

# Reset password if needed
docker-compose exec postgres psql -U postgres -c "ALTER USER ddn_user PASSWORD 'new_password';"
```

## Performance Optimization

### Caching

- Redis caches RAG results (TTL: 3600s)
- LLM responses cached by similarity
- Clear cache: `redis-cli FLUSHALL`

### Async Processing

- Use Celery for long-running tasks
- Implement task retries with exponential backoff
- Monitor with Flower: `http://localhost:5555`

### Logging

- Use structured JSON logging
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Avoid logging sensitive data

## Performance Metrics

Monitor these in Langfuse:

- Agent latency: Goal < 5s for analysis
- RAG latency: Goal < 500ms for retrieval
- LLM latency: Goal < 2s for generation
- Cache hit rate: Target > 40%

## Deployment

See `DEPLOYMENT.md` for production deployment guidelines.

## Support & Questions

- Review existing documentation in `/docs`
- Check GitHub issues and discussions
- Review code comments and docstrings
- Ask maintainers via email or issues

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.
