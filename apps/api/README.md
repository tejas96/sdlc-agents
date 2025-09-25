# SDLC Agents API

This is the FastAPI backend for the SDLC Agents system - a comprehensive Software Development Lifecycle management platform.

## Quick Start

```bash
# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
poetry run python manage.py upgrade

# Start development server
make run
# or
poetry run python manage.py run --reload
```

## Documentation

- **API Docs**: http://localhost:8001/docs (when running)
- **Main Project**: See [../README.md](../../README.md) for complete documentation
- **Architecture**: FastAPI + SQLModel + PostgreSQL + Redis

## Key Features

- 🚀 FastAPI with async support
- 🔐 JWT authentication
- 📊 Project management
- 🤖 AI agent orchestration  
- 🔄 Workflow automation
- 🔗 External integrations (GitHub, Jira, Slack)
- 📈 Monitoring and metrics

## Development Commands

```bash
make run          # Start server
make test         # Run tests  
make format       # Format code
make lint         # Lint code
```

For complete setup instructions and documentation, see the [main README](../../README.md).
