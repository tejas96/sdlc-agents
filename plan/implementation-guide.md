# Optima AI - Complete Implementation Guide

## Overview

This guide provides step-by-step instructions to build a complete Optima AI system from scratch, including all technical components, configurations, and deployment procedures. Follow this guide to create an identical system with all features and capabilities.

## Prerequisites & System Requirements

### Development Environment
- **Node.js**: 18.0.0 or higher
- **Python**: 3.11 or higher
- **Package Managers**: pnpm 8.0.0+, Poetry 1.6.0+
- **Database**: PostgreSQL 15+
- **Docker**: Latest version (optional but recommended)
- **Git**: Latest version

### External Dependencies
- **Anthropic API Key**: For Claude AI integration
- **Development Tools**: VS Code, PyCharm, or similar IDE

## Step 1: Project Structure Setup

### 1.1 Create Monorepo Structure

```bash
# Create root directory
mkdir optima-ai
cd optima-ai

# Create monorepo structure
mkdir -p apps/{api,web}
mkdir -p packages docs tools
mkdir -p apps/api/{app,tests,alembic,seeds,scripts,workspaces}
mkdir -p apps/web/src/{app,components,hooks,lib,services,stores,types}

# Initialize git repository
git init
```

### 1.2 Root Configuration Files

Create `package.json`:
```json
{
  "name": "optima-ai",
  "version": "1.0.0",
  "private": true,
  "description": "Optima AI - FastAPI + Next.js Monorepo with Claude Integration",
  "scripts": {
    "dev": "concurrently \"pnpm run dev:api\" \"pnpm run dev:web\"",
    "dev:web": "pnpm --filter @optima-ai/web dev",
    "dev:api": "cd apps/api && make run HOST=0.0.0.0 PORT=8000 RELOAD=true",
    "build": "turbo run build",
    "test": "turbo run test",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "concurrently": "^8.2.0",
    "turbo": "^1.10.0"
  },
  "packageManager": "pnpm@8.6.0"
}
```

Create `pnpm-workspace.yaml`:
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

Create `turbo.json`:
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "tests/**/*.py"]
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "type-check": {
      "dependsOn": ["^type-check"]
    }
  }
}
```

## Step 2: Backend API Implementation

### 2.1 Python Environment Setup

```bash
cd apps/api

# Initialize Poetry project
poetry init --name optima-ai-api --version 1.0.0 --description "FastAPI backend for Optima AI"
```

### 2.2 Dependencies Configuration

Edit `apps/api/pyproject.toml`:
```toml
[tool.poetry]
name = "optima-ai-api"
version = "1.0.0"
description = "FastAPI backend for Optima AI with Claude Code SDK streaming"
authors = ["Your Team <team@yourcompany.com>"]
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "0.115.12"
uvicorn = {extras = ["standard"], version = "0.24.0"}
python-multipart = "^0.0.9"
pydantic = {extras = ["email"], version = "^2.11.7"}
pydantic-settings = "^2.7.0"
claude-code-sdk = "0.0.20"
sse-starlette = "3.0.2"
httpx = "^0.28.1"
loguru = "^0.7.2"
sqlmodel = "^0.0.14"
sqlalchemy-utils = "^0.41.1"
asyncpg = "^0.30.0"
alembic = "^1.13.1"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
bcrypt = "4.0.1"
click = "^8.1.0"
typer = {extras = ["all"], version = "0.8.0"}
fastmcp = "^2.11.3"
jinja2 = "^3.1.2"
greenlet = "^3.2.4"
pyjwt = "^2.10.1"
python-dotenv = "^1.1.0"

[tool.poetry.group.dev.dependencies]
pytest = "7.4.3"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
isort = "^5.12.0"
mypy = "^1.5.0"
ruff = "^0.1.0"
```

### 2.3 Core Application Structure

Create `apps/api/app/main.py`:
```python
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import close_db_connection
from app.utils import configure_logging, get_logger

logger = get_logger(__name__)

def get_application() -> FastAPI:
    configure_logging()
    settings = get_settings()

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Optima AI - Claude Code Wrapper API",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_DOCS else None,
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    )

    # CORS middleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins() or ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include API router
    _app.include_router(api_router, prefix=settings.API_V1_STR)

    @_app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Starting up application...")
        from app.agents import workflows

    @_app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("Shutting down application...")
        await close_db_connection()

    @_app.get("/")
    async def root() -> dict[str, Any]:
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": "/docs" if settings.ENABLE_DOCS else None,
        }

    @_app.get("/health")
    async def health_check() -> dict[str, Any]:
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "service": "Claude Code Wrapper API",
        }

    return _app

app = get_application()
```

### 2.4 Configuration System

Create `apps/api/app/core/config.py`:
```python
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Paths:
    ROOT_DIR = Path(__file__).resolve().parents[2]
    API_DIR = ROOT_DIR
    APP_DIR = ROOT_DIR / "app"

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = Field(default="Optima AI API")
    VERSION: str = Field(default="1.0.0")
    API_V1_STR: str = Field(default="/api/v1")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: str = Field(default="*")

    # Database Configuration
    DATABASE_URL: str = Field(description="Database connection URL")
    DATABASE_ECHO: bool = Field(default=True)

    # JWT Configuration
    SECRET_KEY: str = Field(description="Secret key for JWT token generation")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Claude Configuration
    ANTHROPIC_API_KEY: str = Field(default="")
    CLAUDE_PERMISSION_MODE: str = Field(default="bypassPermissions")
    CLAUDE_REQUEST_TIMEOUT: int = Field(default=300)

    # Environment Configuration
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    PORT: int = Field(default=8000)

    # Documentation Configuration
    ENABLE_DOCS: bool = Field(default=True)
    ENABLE_REDOC: bool = Field(default=True)

    def get_cors_origins(self) -> list[str]:
        if self.BACKEND_CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=str(Paths.ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 2.5 Database Models

Create `apps/api/app/models/base.py`:
```python
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlmodel import Field, SQLModel

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": func.now()}
    )

class AuditedModel(BaseModel):
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
```

Create `apps/api/app/models/user.py`:
```python
from enum import Enum
from sqlalchemy import Column, String
from sqlalchemy_utils import StringEncryptedType
from sqlmodel import Field
from app.models.base import BaseModel
from app.core.config import get_settings

class Provider(str, Enum):
    PASS = "PASS"
    GITHUB = "GITHUB"
    MICROSOFT = "MICROSOFT"

def get_secret_key() -> str:
    return get_settings().SECRET_KEY

class User(BaseModel, table=True):
    __tablename__ = "users"

    name: str = Field(max_length=255)
    password: Optional[str] = Field(
        sa_column=Column(StringEncryptedType(String(8), key=get_secret_key), nullable=True),
        default=None,
    )
    provider: Provider = Field(default=Provider.PASS)
    email: str = Field(max_length=255, unique=True, index=True)
    is_active: bool = Field(default=True)
```

### 2.6 Database Configuration

Create `apps/api/app/core/database.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def close_db_connection() -> None:
    await engine.dispose()
```

### 2.7 Alembic Setup

Create `apps/api/alembic.ini`:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url =

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `apps/api/alembic/env.py`:
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import get_settings
from app.models import *  # Import all models

settings = get_settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from sqlmodel import SQLModel
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2.8 API Routes Structure

Create `apps/api/app/api/v1/api.py`:
```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, agents, code_assistance, integrations

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["AI Agents"],
)

api_router.include_router(
    code_assistance.router,
    prefix="/claude-code",
    tags=["Claude Code Assistance"],
)

api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"],
)
```

### 2.9 Management CLI

Create `apps/api/manage.py`:
```python
import asyncio
import typer
import uvicorn
from app.core.config import get_settings
from app.core.database import engine
from sqlmodel import SQLModel

app = typer.Typer()

@app.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
):
    """Run the FastAPI server."""
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )

@app.command()
def upgrade():
    """Run database migrations."""
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"])

@app.command()
def current():
    """Show current migration."""
    import subprocess
    subprocess.run(["alembic", "current"])

@app.command()
def revision(message: str):
    """Create new migration."""
    import subprocess
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])

if __name__ == "__main__":
    app()
```

### 2.10 AI Agent System

Create `apps/api/app/agents/enums.py`:
```python
from enum import Enum

class AgentIdentifier(str, Enum):
    CODE_ANALYSIS = "code_analysis"
    TEST_CASE_GENERATION = "test_case_generation"
    REQUIREMENTS_TO_TICKETS = "requirements_to_tickets"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    CODE_REVIEWER = "code_reviewer"

class AgentModule(str, Enum):
    DEVELOPMENT = "development"
    PROJECT_MANAGEMENT = "project_management"
    QUALITY_ASSURANCE = "quality_assurance"
```

Create `apps/api/app/agents/workflows/base.py`:
```python
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from app.agents.enums import AgentIdentifier

class AgentWorkflow(ABC):
    identifier: AgentIdentifier | None = None

    def __init__(
        self,
        *,
        workspace_dir: Path,
        mcp_configs: dict[str, Any],
        integration_service: Any,
        system_prompt: str | None = None,
        llm_session_id: str | None = None,
    ) -> None:
        self.workspace_dir = workspace_dir
        self.mcp_configs = mcp_configs
        self.integration_service = integration_service
        self.system_prompt = system_prompt
        self.llm_session_id = llm_session_id

    @abstractmethod
    def run(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Execute the agent workflow and stream responses."""
        ...

    @abstractmethod
    def prepare(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Perform pre-steps before orchestration."""
        ...

    @abstractmethod
    def finalize(self, *, session: Any, messages: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """Perform post-steps after orchestration."""
        ...
```

## Step 3: Frontend Implementation

### 3.1 Next.js Setup

```bash
cd apps/web

# Initialize Next.js project
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

### 3.2 Package Configuration

Edit `apps/web/package.json`:
```json
{
  "name": "@optima-ai/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --build",
    "test": "vitest --reporter=verbose"
  },
  "dependencies": {
    "@ai-sdk/react": "^1.2.12",
    "@radix-ui/react-dropdown-menu": "^2.1.15",
    "@radix-ui/react-label": "^2.1.7",
    "@radix-ui/react-slot": "^1.2.3",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.525.0",
    "next": "15.4.3",
    "react": "19.1.0",
    "react-dom": "19.1.0",
    "sonner": "^2.0.7",
    "tailwind-merge": "^3.3.1",
    "zustand": "^5.0.6"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19.1.8",
    "@types/react-dom": "^19.1.6",
    "eslint": "^9",
    "eslint-config-next": "15.4.3",
    "typescript": "^5",
    "vitest": "^3.2.4"
  }
}
```

### 3.3 Core Layout

Create `apps/web/src/app/layout.tsx`:
```tsx
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Optima AI - Intelligent Development Assistant',
  description: 'Your intelligent development assistant for enhanced productivity and code quality',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang='en'>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Toaster richColors position='top-right' expand />
        {children}
      </body>
    </html>
  );
}
```

### 3.4 Component Structure

Create base UI components using shadcn/ui:
```bash
# Install shadcn/ui
pnpm dlx shadcn@latest init

# Add essential components
pnpm dlx shadcn@latest add button input card dialog
```

### 3.5 State Management

Create `apps/web/src/stores/auth.ts`:
```typescript
import { create } from 'zustand';

interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    // Implement login logic
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const data = await response.json();
      set({
        user: data.user,
        token: data.access_token,
        isAuthenticated: true
      });
    }
  },

  logout: () => {
    set({ user: null, token: null, isAuthenticated: false });
  },

  setUser: (user: User) => {
    set({ user, isAuthenticated: true });
  },
}));
```

## Step 4: Docker Configuration

### 4.1 Backend Dockerfile

Create `apps/api/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create workspace directory
RUN mkdir -p /app/workspaces

EXPOSE 8000

CMD ["python", "manage.py", "run", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Frontend Dockerfile

Create `apps/web/Dockerfile`:
```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm install -g pnpm && pnpm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

### 4.3 Docker Compose

Create `docker-compose.yml`:
```yaml
services:
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - api
    networks:
      - optima_ai_network

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:OptimaAI2024!@postgres:5432/optima_ai
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - optima_ai_network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: optima_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: OptimaAI2024!
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d optima_ai"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - optima_ai_network

volumes:
  postgres_data:

networks:
  optima_ai_network:
    driver: bridge
```

## Step 5: Environment Configuration

### 5.1 Backend Environment

Create `apps/api/.env.example`:
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:OptimaAI2024!@localhost:5432/optima_ai
DATABASE_ECHO=false

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Claude Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key

# API Configuration
PROJECT_NAME=Optima AI API
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=true
ENVIRONMENT=development
PORT=8000

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Workspace Configuration
AGENTS_DIR=/tmp/optima-workspaces
```

### 5.2 Frontend Environment

Create `apps/web/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Step 6: Development Tools Setup

### 6.1 Backend Makefile

Create `apps/api/Makefile`:
```makefile
.PHONY: help run test lint format clean install

# Variables
PYTHON := poetry run python
POETRY := poetry
HOST := 127.0.0.1
PORT := 8000
RELOAD := false

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(POETRY) install

run: ## Run the FastAPI server
	$(PYTHON) manage.py run --host $(HOST) --port $(PORT) $(if $(filter true,$(RELOAD)),--reload)

test: ## Run tests with coverage
	$(POETRY) run pytest --cov=app --cov-report=term-missing

lint: ## Run linting and type checking
	$(POETRY) run ruff check --fix app/
	$(POETRY) run mypy app/

format: ## Format code
	$(POETRY) run isort app/
	$(POETRY) run black app/

clean: ## Clean cache and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

prestart: ## Wait for DB, run migrations, seed data
	$(PYTHON) manage.py upgrade
	$(PYTHON) -c "from seeds.seed_users import seed_users; import asyncio; asyncio.run(seed_users())"

manage: ## Run manage.py command (use ARGS="command")
	$(PYTHON) manage.py $(ARGS)
```

### 6.2 Git Configuration

Create `.gitignore`:
```gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment files
.env
.env.local
.env.production.local

# Build outputs
.next/
dist/
build/

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.coverage
.pytest_cache/

# Workspace
workspaces/
```

## Step 7: Testing Setup

### 7.1 Backend Testing

Create `apps/api/tests/conftest.py`:
```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.main import app
from app.core.database import get_session

# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
```

### 7.2 Frontend Testing

Create `apps/web/vitest.config.mts`:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    globals: true,
  },
});
```

## Step 8: Database Initialization

### 8.1 Create Initial Migration

```bash
cd apps/api

# Initialize Alembic
poetry run alembic init alembic

# Create initial migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migration
poetry run alembic upgrade head
```

### 8.2 Seed Data

Create `apps/api/seeds/seed_users.py`:
```python
import asyncio
from app.core.database import async_session
from app.models.user import User, Provider

async def seed_users():
    async with async_session() as session:
        # Create admin user
        admin_user = User(
            name="Admin User",
            email="admin@optima-ai.com",
            provider=Provider.PASS,
            is_active=True
        )
        session.add(admin_user)
        await session.commit()
        print("Admin user created successfully")

if __name__ == "__main__":
    asyncio.run(seed_users())
```

## Step 9: Development Workflow

### 9.1 Initial Setup Commands

```bash
# Clone or initialize repository
git clone <your-repo-url> optima-ai
cd optima-ai

# Install dependencies
pnpm install
cd apps/api && poetry install && cd ../..

# Set up environment files
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

# Edit environment files with your values
# - Add your Anthropic API key
# - Set secure secret key
# - Configure database URL

# Start PostgreSQL (using Docker)
docker run --name optima-postgres -e POSTGRES_PASSWORD=OptimaAI2024! -e POSTGRES_DB=optima_ai -p 5432:5432 -d postgres:15

# Set up database
cd apps/api
make prestart

# Start development servers
cd ../..
pnpm dev
```

### 9.2 Available Commands

```bash
# Development
pnpm dev              # Start both API and web
pnpm dev:api          # Start only API
pnpm dev:web          # Start only web

# Testing
pnpm test             # Run all tests
cd apps/api && make test    # API tests only
cd apps/web && pnpm test    # Web tests only

# Code quality
cd apps/api && make format  # Format API code
cd apps/api && make lint    # Lint API code
cd apps/web && pnpm lint    # Lint web code

# Database
cd apps/api && make manage ARGS="upgrade"   # Run migrations
cd apps/api && make manage ARGS="revision -m 'description'"  # Create migration

# Docker
pnpm docker:up        # Start all services
pnpm docker:down      # Stop all services
```

## Step 10: Production Deployment

### 10.1 Environment Variables for Production

```bash
# Production API Environment
DATABASE_URL=postgresql+asyncpg://user:password@production-db:5432/optima_ai
SECRET_KEY=production-secret-key-minimum-32-characters-random
ANTHROPIC_API_KEY=your-production-anthropic-key
DEBUG=false
ENVIRONMENT=production
BACKEND_CORS_ORIGINS=https://yourdomain.com
```

### 10.2 Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### 10.3 Health Checks

Monitor these endpoints in production:
- `GET /health` - Application health
- `GET /api/v1/claude-code/health` - AI service health
- Database connection monitoring
- Log aggregation and monitoring

## Step 11: Monitoring & Maintenance

### 11.1 Application Monitoring

Set up monitoring for:
- **Application Performance**: Response times, throughput
- **Database Performance**: Query times, connection pool usage
- **AI Service Performance**: Claude API response times
- **Error Rates**: 4xx/5xx error tracking
- **Business Metrics**: Agent usage, user activity

### 11.2 Regular Maintenance Tasks

```bash
# Database backups
pg_dump optima_ai > backup_$(date +%Y%m%d).sql

# Log rotation and cleanup
find logs/ -name "*.log" -mtime +7 -delete

# Update dependencies
cd apps/api && poetry update
cd apps/web && pnpm update

# Security updates
cd apps/api && poetry audit
cd apps/web && pnpm audit
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Claude API Errors**
   - Verify ANTHROPIC_API_KEY is set
   - Check API key permissions
   - Monitor rate limits

3. **Build Failures**
   - Clear node_modules and reinstall
   - Check Python version compatibility
   - Verify all environment variables

4. **CORS Issues**
   - Update BACKEND_CORS_ORIGINS
   - Check frontend API URL configuration

This implementation guide provides everything needed to build a complete Optima AI system. Follow the steps sequentially, and you'll have a fully functional development assistant platform with AI agents, integrations, and a modern web interface.
