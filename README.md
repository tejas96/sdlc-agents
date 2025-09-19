# SDLC Agent - Intelligent Development Lifecycle

A production-ready, full-stack Software Development Lifecycle (SDLC) management platform built with **FastAPI** backend and **Next.js** frontend. This system provides AI-powered agents, workflow automation, and comprehensive project analytics for managing modern software development processes.

## 🏗️ Architecture

This monorepo follows modern full-stack architecture with clear separation of concerns:

```
sdlc-agents/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py        # FastAPI app entry point
│   │   │   ├── core/          # Configuration and database
│   │   │   ├── api/           # API routes and endpoints
│   │   │   ├── models/        # SQLModel database models
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── crud/          # Database operations
│   │   │   └── utils/         # Utility functions
│   │   ├── tests/             # API test suite
│   │   ├── alembic/           # Database migrations
│   │   └── pyproject.toml     # Poetry dependencies
│   └── web/                   # Next.js frontend
│       ├── src/
│       │   ├── app/           # Next.js App Router
│       │   ├── components/    # React components
│       │   ├── hooks/         # React Query hooks
│       │   ├── lib/           # API client & utilities
│       │   ├── services/      # Business logic
│       │   ├── stores/        # State management
│       │   └── types/         # TypeScript types
│       ├── public/            # Static assets
│       └── package.json       # pnpm dependencies
├── docker-compose.yml        # Full-stack orchestration
├── pnpm-workspace.yaml       # Workspace configuration
└── README.md                 # This file
```

### System Architecture

```mermaid
graph TB
    %% User Interface
    USER["`**👤 Developer/Team**
    *SDLC Management Requests*`"]

    %% Backend Services (Current)
    subgraph "🚀 Backend API"
        FASTAPI["`**FastAPI Server**
        *Python 3.11 + Async*`"]
        ROUTER["`**API Router**
        *v1/projects, agents, workflows*`"]
        AUTH["`**Authentication**
        *JWT + User Management*`"]
    end

    %% Core Features
    subgraph "📋 Project Management"
        PROJECTS["`**Projects**
        *Repository Integration*`"]
        WORKFLOWS["`**Workflows**
        *Automated Processes*`"]
        AGENTS["`**AI Agents**
        *Task Automation*`"]
    end

    %% Integrations
    subgraph "🔗 Integrations"
        GITHUB["`**GitHub**
        *Repository Management*`"]
        JIRA["`**Jira**
        *Issue Tracking*`"]
        SLACK["`**Slack**
        *Team Communication*`"]
    end

    %% Data Layer
    subgraph "💾 Data Layer"
        POSTGRES["`**PostgreSQL**
        *Primary Database*`"]
        REDIS["`**Redis**
        *Caching & Queues*`"]
    end

    %% Current Active Flow
    USER --> FASTAPI
    FASTAPI --> ROUTER
    ROUTER --> AUTH
    ROUTER --> PROJECTS
    ROUTER --> WORKFLOWS
    ROUTER --> AGENTS
    
    PROJECTS --> GITHUB
    WORKFLOWS --> JIRA
    AGENTS --> SLACK
    
    FASTAPI --> POSTGRES
    FASTAPI --> REDIS

    %% Styling
    classDef userStyle fill:#2D3748,color:#ffffff,stroke:#4A5568,stroke-width:3px,font-weight:bold
    classDef backendStyle fill:#38A169,color:#ffffff,stroke:#2F855A,stroke-width:2px,font-weight:bold
    classDef featureStyle fill:#3182CE,color:#ffffff,stroke:#2B6CB0,stroke-width:2px,font-weight:bold
    classDef integrationStyle fill:#ED8936,color:#ffffff,stroke:#DD6B20,stroke-width:2px,font-weight:bold
    classDef dataStyle fill:#9F7AEA,color:#ffffff,stroke:#805AD5,stroke-width:2px,font-weight:bold

    %% Apply Styles
    class USER userStyle
    class FASTAPI,ROUTER,AUTH backendStyle
    class PROJECTS,WORKFLOWS,AGENTS featureStyle
    class GITHUB,JIRA,SLACK integrationStyle
    class POSTGRES,REDIS dataStyle
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ with **pnpm** (for frontend)
- **Python** 3.11+ with **Poetry** (for backend)
- **Docker** (recommended for database and full-stack development)
- **PostgreSQL** (for production, included in Docker setup)

### Installation

#### 1. Install Node.js 18+ and pnpm

**Option A: Using Node Version Manager (recommended)**

```bash
# Install nvm (on macOS/Linux)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js 18
nvm install 18
nvm use 18

# Install pnpm
npm install -g pnpm
```

**Option B: Direct installation**

- Visit [nodejs.org](https://nodejs.org/) and download Node.js 18+
- Install pnpm: `npm install -g pnpm`

#### 2. Install Python 3.11+

**Option A: Using pyenv (recommended)**

```bash
# Install pyenv (on macOS/Linux)
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.5
pyenv global 3.11.5
```

**Option B: Direct installation**

- Visit [python.org](https://python.org/) and download Python 3.11+
- Or use package managers:

  ```bash
  # macOS with Homebrew
  brew install python@3.11

  # Ubuntu/Debian
  sudo apt update && sudo apt install python3.11 python3.11-pip

  # Windows with Chocolatey
  choco install python311
  ```

#### 2. Install Poetry

**Option A: Official installer (recommended)**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Option B: Using pip**

```bash
pip install poetry
```

**Verify Poetry installation:**

```bash
poetry --version  # Should show 1.6.0 or higher
```

#### 3. Install Docker (Optional)

- Visit [docker.com](https://www.docker.com/get-started) and download Docker Desktop
- Or use package managers:

  ```bash
  # macOS with Homebrew
  brew install --cask docker

  # Ubuntu/Debian
  sudo apt update && sudo apt install docker.io docker-compose

  # Windows with Chocolatey
  choco install docker-desktop
  ```

### Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd sdlc-agents
   ```

2. **Verify installations**

   ```bash
   # Check all prerequisites
   node --version      # Should be 18+
   pnpm --version      # Should be 8+
   python --version    # Should be 3.11+
   poetry --version    # Should be 1.6+
   docker --version    # Optional but recommended
   ```

3. **Install dependencies**

   ```bash
   # Install frontend dependencies
   cd apps/web
   pnpm install

   # Install backend dependencies
   cd ../api
   poetry install

   # Return to root for workspace commands
   cd ../..
   ```

4. **Set up environment variables**

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env with your configuration
   nano .env  # or use your preferred editor
   ```

   **Required environment variables:**
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/sdlc_agents
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ```

5. **Set up the database**

   **Option A: Using Docker (recommended for development)**

   ```bash
   # Start PostgreSQL with Docker Compose
   cd ../..  # Back to root directory
   docker-compose up postgres -d

   # Initialize database
   cd apps/api
   poetry run python manage.py upgrade
   ```

   **Option B: Local PostgreSQL**

   ```bash
   # Install PostgreSQL locally
   # Create database
   createdb sdlc_agents

   # Run migrations
   poetry run python manage.py upgrade
   ```

6. **Create initial user** (Optional)

   ```bash
   poetry run python manage.py create-user \
     --email admin@example.com \
     --username admin \
     --password admin123 \
     --full-name "Admin User" \
     --is-superuser
   ```

7. **Start the development servers**

   **Option A: Full-stack development (recommended)**

   ```bash
   # Start both API and Web servers
   pnpm dev
   ```

   **Option B: Individual services**

   ```bash
   # Terminal 1: Start API server
   pnpm dev:api

   # Terminal 2: Start Web server  
   pnpm dev:web
   ```

   **Option C: Using Docker**

   ```bash
   # Start all services with Docker
   pnpm docker:up
   ```

8. **Verify setup**

   ```bash
   # Test API health endpoint
   curl http://localhost:8001/health

   # Test Web application
   curl http://localhost:3000
   ```

   **Access the applications:**
   - **Frontend**: http://localhost:3000 (Next.js app)
   - **Backend API**: http://localhost:8001 (FastAPI)
   - **API Docs**: http://localhost:8001/docs (Swagger UI)
   - **ReDoc**: http://localhost:8001/redoc (Alternative docs)

### Using Docker (Alternative Setup)

If you prefer containerized development:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 📚 API Documentation

Once the API is running, visit:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/api/v1/openapi.json

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

#### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Agents
- `GET /api/v1/agents/` - List AI agents
- `POST /api/v1/agents/` - Create agent
- `POST /api/v1/agents/{id}/execute` - Execute agent

#### Workflows
- `GET /api/v1/workflows/` - List workflows
- `POST /api/v1/workflows/` - Create workflow
- `POST /api/v1/workflows/{id}/trigger` - Trigger workflow

#### Integrations
- `GET /api/v1/integrations/` - List integrations
- `POST /api/v1/integrations/` - Create integration
- `POST /api/v1/integrations/{id}/test` - Test integration

#### Monitoring
- `GET /api/v1/monitoring/health` - System health
- `GET /api/v1/monitoring/stats` - User statistics
- `GET /api/v1/monitoring/metrics` - Performance metrics

### Example Usage

#### Register and Login

```bash
# Register a new user
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "securepassword123",
    "full_name": "New User"
  }'

# Login
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Create a Project

```bash
# Create project (requires JWT token)
curl -X POST "http://localhost:8001/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My SDLC Project",
    "slug": "my-sdlc-project",
    "description": "A sample project for testing",
    "project_type": "web_app",
    "repository_url": "https://github.com/user/my-project"
  }'
```

## 🧪 Testing

### Full-Stack Testing

```bash
# Run all tests (API + Web)
pnpm test

# Run API tests only
pnpm test:api

# Run Web tests only  
pnpm test:web
```

### Backend Testing (FastAPI)

```bash
cd apps/api

# Run all tests
make test

# Run tests with coverage
poetry run pytest --cov=app --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_auth.py -v

# Run tests with database
poetry run pytest tests/ -v --tb=short
```

### Frontend Testing (Next.js)

```bash
cd apps/web

# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with UI
pnpm test:ui

# Type checking
pnpm type-check
```

## 🎨 Code Quality

The project includes comprehensive code quality tools:

```bash
# Format code
make format

# Lint code
make lint

# Type checking
poetry run mypy app/

# All quality checks
poetry run ruff check app/
poetry run black app/ --check
poetry run isort app/ --check
poetry run mypy app/
```

## 🐳 Docker Development

### Build and Run

```bash
# Build the API image
docker build -t sdlc-agents-api ./apps/api

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Execute commands in container
docker-compose exec api poetry run python manage.py upgrade
```

### Environment Variables in Docker

The `docker-compose.yml` includes environment variables for:

- Database connections
- Application settings
- Service configuration

## 🚀 Deployment

### Environment Setup

1. **Production Environment Variables**

   ```bash
   # Production settings
   ENVIRONMENT=production
   DEBUG=false
   DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/sdlc_agents
   SECRET_KEY=your-production-secret-key
   ```

2. **Database Migrations**

   ```bash
   # Apply migrations in production
   poetry run python manage.py upgrade
   ```

3. **Create Superuser**

   ```bash
   # Create admin user for production
   poetry run python manage.py create-user \
     --email admin@yourdomain.com \
     --username admin \
     --password secure_password \
     --is-superuser
   ```

### CI/CD Pipeline

The project includes GitHub Actions workflows:

- **Code Quality**: Runs linting, type checking, and tests
- **Deploy**: Builds and deploys on main branch changes

## 🛠️ Development Commands

### Management Commands

```bash
# Database operations
python manage.py upgrade          # Apply migrations
python manage.py downgrade        # Rollback migrations
python manage.py revision -m "msg" # Create new migration
python manage.py current          # Show current revision
python manage.py history          # Show migration history

# User management
python manage.py create-user --email user@example.com --username user --password pass

# Server operations
python manage.py run              # Start server
python manage.py run --reload     # Start with auto-reload
python manage.py run --host 0.0.0.0 --port 8001
```

### Makefile Commands

```bash
make run                 # Start development server
make test                # Run tests
make format              # Format code (isort + black)
make lint                # Lint code (ruff + mypy)
make clean               # Clean cache files
```

## 🎯 Features

### Current Features

**Backend (FastAPI)**
- ✅ FastAPI backend with async support
- ✅ User authentication with JWT tokens  
- ✅ Project management and tracking
- ✅ AI agent creation and management
- ✅ Workflow definition and orchestration
- ✅ Integration management (GitHub, Jira, Slack)
- ✅ RESTful API with comprehensive documentation
- ✅ Database migrations with Alembic
- ✅ Comprehensive test suite with pytest

**Frontend (Next.js)**
- ✅ Modern Next.js 15 with App Router
- ✅ TypeScript for type safety
- ✅ Tailwind CSS with custom design system
- ✅ React Query for data fetching
- ✅ Glass morphism UI inspired by design.html
- ✅ Responsive design (mobile-first)
- ✅ Component library (Button, Card, Table, Modal, etc.)
- ✅ Dashboard with real-time stats
- ✅ Agent management interface
- ✅ Project tracking views
- ✅ Comprehensive testing with Vitest

**DevOps & Infrastructure**
- ✅ Docker containerization for both services
- ✅ Docker Compose for full-stack development
- ✅ pnpm workspace for monorepo management
- ✅ Code quality tools and linting
- ✅ Health monitoring and metrics

### Planned Features

- 🔄 Agent execution engine
- 🔄 Workflow runtime and scheduling
- 🔄 Real-time notifications
- 🔄 Advanced analytics dashboard
- 🔄 Plugin system for custom integrations
- 🔄 Kubernetes deployment configs
- 🔄 Advanced user roles and permissions

## 🛠️ Technology Stack

### Backend (FastAPI)

- **FastAPI** - Modern, fast web framework for Python
- **SQLModel** - SQL databases using Python type hints
- **Alembic** - Database migration tool
- **PostgreSQL** - Primary database
- **Redis** - Caching and message queuing
- **Poetry** - Dependency management
- **pytest** - Testing framework

### Frontend (Next.js)

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS v4** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **Headless UI** - Accessible UI components
- **Heroicons** - Beautiful hand-crafted SVG icons
- **Recharts** - Composable charting library
- **Vitest** - Fast unit testing framework
- **React Testing Library** - Simple testing utilities

### DevOps & Tools

- **Docker** - Containerization for both services
- **pnpm** - Fast, disk space efficient package manager
- **Turborepo** - High-performance build system
- **ESLint** & **Prettier** - Code linting and formatting
- **Black** & **isort** - Python code formatting
- **Ruff** - Fast Python linter
- **mypy** - Static type checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`make test`)
5. Format and lint your code (`make format lint`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive tests
- Document all public APIs
- Keep line length to 120 characters

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Built with ❤️ by the SDLC Agents Team

## 📞 Support

- **Documentation**: Check this README and API docs
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

For more detailed information about specific components, see the inline documentation and API specifications at `/docs` when running the server.
