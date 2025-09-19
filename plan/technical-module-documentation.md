# Optima AI - Technical Module Documentation

## System Overview

**Optima AI** is a comprehensive intelligent development assistant platform that provides AI-powered code analysis, quality assurance, and project management capabilities. The system is built as a modern full-stack application with a FastAPI backend, Next.js frontend, and PostgreSQL database.

## Architecture & Technology Stack

### Core Architecture
The system follows a **monorepo architecture** with clear separation of concerns:

```
optima-ai/
├── apps/
│   ├── api/          # FastAPI Backend
│   └── web/          # Next.js Frontend
├── packages/         # Shared libraries
├── docs/            # Documentation
└── tools/           # Development tools
```

### Technology Stack

#### Backend (apps/api/)
- **Framework**: FastAPI 0.115.12 with async/await support
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with SQLModel ORM
- **Authentication**: JWT-based with refresh tokens
- **AI Integration**: Claude Code SDK 0.0.20 (Anthropic)
- **MCP Support**: FastMCP 2.11.3 for external integrations
- **Migration**: Alembic for database schema management
- **Dependency Management**: Poetry
- **Container Runtime**: Docker with health checks

#### Frontend (apps/web/)
- **Framework**: Next.js 15.4.3 with App Router
- **Language**: TypeScript 5
- **UI Library**: Shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **Icons**: Lucide React + Phosphor Icons
- **Testing**: Vitest with Testing Library
- **Build Tool**: Turbopack for development

#### Development Tools
- **Package Manager**: pnpm 8+ for monorepo management
- **Build System**: Turborepo for optimized builds
- **Code Quality**: ESLint, Prettier, Black, isort, Ruff
- **Type Checking**: TypeScript (frontend), MyPy (backend)
- **Testing**: Vitest (frontend), pytest (backend)

## Database Architecture

### Core Schema Design

#### User Management
```sql
-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255), -- Encrypted with StringEncryptedType
    provider VARCHAR(20) DEFAULT 'PASS', -- PASS/GITHUB/MICROSOFT
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### AI Agents System
```sql
-- AI Agents table
CREATE TABLE ai_agents (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    identifier VARCHAR(50) UNIQUE NOT NULL, -- Workflow type
    module VARCHAR(50) NOT NULL, -- DEVELOPMENT/PROJECT_MANAGEMENT/QUALITY_ASSURANCE
    tags JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    custom_properties_schema JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User Agent Sessions table
CREATE TABLE user_agent_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    agent_id BIGINT REFERENCES ai_agents(id),
    project_id BIGINT REFERENCES projects(id),
    session_name VARCHAR(255),
    mcps JSONB DEFAULT '[]', -- MCP configurations
    custom_properties JSONB DEFAULT '{}',
    llm_session_id VARCHAR(255), -- Claude session tracking
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Integration Management
```sql
-- Integrations table
CREATE TABLE integrations (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    auth_type VARCHAR(20) NOT NULL, -- oauth/api_key/pat
    credentials JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    type VARCHAR(50) NOT NULL, -- github/atlassian/notion/sentry/etc
    created_by BIGINT REFERENCES users(id),
    updated_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Business rule: One integration per type per user
    CONSTRAINT uq_integration_type_user UNIQUE (type, created_by)
);
```

### Migration History
The system uses Alembic for database migrations with the following evolution:
1. **20250808_1733_initial.py** - Base schema setup
2. **20250809_1644_create_integrations_table.py** - Integration system
3. **20250811_1723_agents.py** - AI agents core
4. **20250812_1122_llm_session_id_col.py** - LLM session tracking
5. **20250812_1354_add_integration_unique_constraints.py** - Business rules
6. **20250820_2053_add_agent_identifier.py** - Agent workflow types
7. **20250826_1324_remove_mcp_config_from_integrations.py** - MCP refactoring
8. **20250902_0737_add_code_review_in_agent_identifier.py** - Code review workflows
9. **20250908_1138_add_integration_providers_and_new_agent.py** - Extended integrations

## API Architecture

### Authentication System
```python
# JWT-based authentication with refresh tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

# Endpoints
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # Login with JWT tokens
POST /api/v1/auth/refresh     # Refresh access token
GET  /api/v1/auth/me          # Current user info
```

### Core API Endpoints

#### AI Agents
```python
GET    /api/v1/agents                    # List available agents
GET    /api/v1/agents/{agent_id}         # Agent details
POST   /api/v1/agents/{agent_id}/run     # Execute agent workflow
POST   /api/v1/agents/{agent_id}/session # Create agent session
```

#### Code Assistance
```python
POST   /api/v1/claude-code/code-assistance  # Streaming code help
GET    /api/v1/claude-code/health           # Service health check
```

#### Integrations
```python
GET    /api/v1/integrations                    # User integrations
POST   /api/v1/integrations                    # Create integration
PUT    /api/v1/integrations/{integration_id}   # Update integration
DELETE /api/v1/integrations/{integration_id}   # Delete integration

# Integration utility endpoints
GET    /api/v1/integrations/{provider}/repositories  # GitHub repos
GET    /api/v1/integrations/{provider}/spaces        # Confluence spaces
GET    /api/v1/integrations/{provider}/projects      # Jira projects
```

#### File Management
```python
POST   /api/v1/files/upload               # Upload files
GET    /api/v1/files/{session_id}         # List session files
DELETE /api/v1/files/{file_id}            # Delete file
```

## AI Agent System

### Agent Types & Capabilities

#### 1. Code Analysis Agent (`CODE_ANALYSIS`)
- **Module**: Development
- **Purpose**: Comprehensive code documentation generation
- **Features**:
  - Multi-language support
  - API documentation generation
  - README file creation
  - Inline code comments
  - Architecture analysis

#### 2. Test Case Generation Agent (`TEST_CASE_GENERATION`)
- **Module**: Quality Assurance
- **Purpose**: Automated test case creation
- **Features**:
  - Unit test generation
  - Integration test creation
  - Coverage analysis
  - Mock generation
  - Multiple test frameworks (pytest, jest, junit, etc.)

#### 3. Requirements to Tickets Agent (`REQUIREMENTS_TO_TICKETS`)
- **Module**: Project Management
- **Purpose**: Convert requirements to structured tickets
- **Features**:
  - PRD analysis
  - JIRA ticket creation
  - Epic/Story/Task breakdown
  - Priority estimation
  - Acceptance criteria generation

#### 4. Code Reviewer Agent (`CODE_REVIEWER`)
- **Module**: Development
- **Purpose**: Automated pull request review
- **Features**:
  - Code quality analysis
  - Best practices checking
  - Security vulnerability detection
  - Performance optimization suggestions

#### 5. Root Cause Analysis Agent (`ROOT_CAUSE_ANALYSIS`)
- **Module**: Development
- **Purpose**: Incident analysis and debugging
- **Features**:
  - Log analysis
  - Error tracking
  - Code correlation
  - Fix suggestions

### Agent Workflow Architecture

```python
class AgentWorkflow(ABC):
    """Base protocol for all agent workflows"""

    # Core lifecycle methods
    async def prepare()   # Pre-execution setup
    async def run()      # Main execution
    async def finalize() # Post-execution cleanup

    # Template rendering
    async def _prepare_system_prompt()
    async def _prepare_user_prompt()
    async def _prepare_user_followup_prompt()
```

Each agent follows a structured workflow:
1. **Preparation**: Workspace setup, file copying, integration initialization
2. **Execution**: Claude orchestration with streaming responses
3. **Finalization**: Artifact saving, cleanup, result processing

### MCP Integration Architecture

The system supports **Model Context Protocol (MCP)** for external tool integration:

```json
{
  "atlassian": {
    "type": "sse",
    "url": "https://mcp.atlassian.com/v1/sse",
    "headers": { "Authorization": "Bearer TOKEN" }
  },
  "notion": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "OPENAPI_MCP_HEADERS": "{...}" }
  }
}
```

## Integration System

### Supported Providers

#### Development & Version Control
- **GitHub**: Repository management, PR analysis, code review
- **GitLab**: Similar to GitHub capabilities

#### Documentation & Knowledge Management
- **Atlassian (Jira/Confluence)**: Ticket management, documentation
- **Notion**: Knowledge base, documentation
- **Figma**: Design documentation integration

#### Monitoring & Observability
- **Sentry**: Error tracking and monitoring
- **DataDog**: Metrics and observability
- **PagerDuty**: Incident management
- **CloudWatch**: AWS monitoring
- **Grafana**: Visualization and dashboards
- **New Relic**: Application performance monitoring

### Authentication Types
- **OAuth**: Full OAuth 2.0 flow with refresh tokens
- **API Key**: Simple API key authentication
- **PAT**: Personal Access Tokens

### Integration Capabilities
Each integration exposes specific capabilities:
- `repositories`, `branches`, `pull_requests` (GitHub)
- `pages`, `spaces` (Confluence)
- `projects`, `issues` (Jira)
- `incidents`, `errors`, `metrics`, `logs`, `alerts` (Monitoring tools)

## Configuration Management

### Environment Configuration
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/optima_ai
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Integration
ANTHROPIC_API_KEY=your-api-key
CLAUDE_PERMISSION_MODE=bypassPermissions
CLAUDE_REQUEST_TIMEOUT=300

# Application
PORT=8000
DEBUG=true
ENVIRONMENT=development
AGENTS_DIR=/app/workspaces/
```

### Development Workflow

#### Backend Development
```bash
# Setup
cd apps/api
poetry install
poetry shell

# Development
make run              # Start server
make test             # Run tests
make format           # Format code
make lint             # Lint code

# Database
make prestart         # Setup DB
python manage.py upgrade     # Run migrations
python manage.py revision    # Create migration
```

#### Frontend Development
```bash
# Setup
cd apps/web
pnpm install

# Development
pnpm dev              # Start dev server
pnpm test             # Run tests
pnpm lint             # Lint code
pnpm type-check       # Type checking
```

#### Full Stack Development
```bash
# Root level commands
pnpm dev              # Both API and web
pnpm test             # All tests
pnpm docker:up        # Docker stack
```

## Deployment Architecture

### Docker Configuration
```yaml
# docker-compose.yml
services:
  api:
    build: ./apps/api
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:OptimaAI2024!@host.docker.internal:5435/optima_ai
    depends_on:
      postgres:
        condition: service_healthy

  web:
    build: ./apps/web
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on: [api]

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: optima_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: OptimaAI2024!
    ports: ["5435:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d optima_ai"]
```

### Production Considerations
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session management (recommended)
- **Load Balancing**: Nginx for API and static assets
- **Monitoring**: Health checks and logging
- **Security**: HTTPS, CORS configuration, rate limiting

## Frontend Architecture

### Component Structure
```
src/
├── app/                    # Next.js App Router
├── components/
│   ├── ui/                # Base UI components (Shadcn)
│   ├── features/          # Feature-specific components
│   │   ├── chat/          # AI chat interface
│   │   ├── code-review/   # Code review features
│   │   ├── quality-assurance/  # QA tools
│   │   └── product-management/ # PM tools
│   ├── shared/            # Shared components
│   └── icons/             # Icon components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities and configurations
├── services/              # API client services
├── stores/                # Zustand state management
└── types/                 # TypeScript definitions
```

### Key Features
- **Real-time Chat**: Streaming AI responses with SSE
- **File Upload**: Multi-file support with drag & drop
- **Integration Management**: OAuth flows and configuration
- **Agent Configuration**: Dynamic form generation based on schemas
- **Repository Selection**: GitHub/GitLab integration
- **Document Management**: Confluence/Notion integration

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Short-lived access tokens (30 min) + long-lived refresh tokens (7 days)
- **Password Encryption**: SQLAlchemy StringEncryptedType with secret key
- **OAuth Integration**: Secure OAuth 2.0 flows for external services
- **Session Management**: Server-side session tracking

### Data Protection
- **Database Encryption**: Sensitive fields encrypted at rest
- **API Security**: Rate limiting, request size limits (10MB)
- **CORS Configuration**: Proper origin restrictions
- **Input Validation**: Pydantic schemas for all inputs

## Testing Strategy

### Backend Testing
- **Unit Tests**: pytest with asyncio support
- **Integration Tests**: Database and API endpoint testing
- **Coverage**: Comprehensive test coverage with pytest-cov
- **Mocking**: External service mocking for isolation

### Frontend Testing
- **Unit Tests**: Vitest with Testing Library
- **Component Tests**: React component testing
- **E2E Testing**: Playwright integration (planned)

## Performance Considerations

### Database Optimization
- **Connection Pooling**: Configurable pool size and overflow
- **Query Optimization**: SQLModel ORM with async queries
- **Indexing**: Strategic indexes on frequently queried fields
- **Migration Management**: Alembic for schema evolution

### API Performance
- **Async Operations**: FastAPI with async/await throughout
- **Streaming**: Server-Sent Events for real-time responses
- **Request Validation**: Pydantic for efficient validation
- **Caching**: Response caching for static data (recommended)

### Frontend Performance
- **Build Optimization**: Turbopack for fast development builds
- **Code Splitting**: Next.js automatic code splitting
- **Asset Optimization**: Image optimization and lazy loading
- **State Management**: Efficient Zustand store updates

## Monitoring & Observability

### Application Monitoring
- **Health Checks**: Comprehensive health endpoints
- **Logging**: Structured logging with Loguru
- **Error Tracking**: Integration-ready for Sentry
- **Metrics**: Application performance metrics

### Development Tools
- **Hot Reload**: Development server with auto-reload
- **Type Safety**: Full TypeScript and MyPy coverage
- **Code Quality**: Automated linting and formatting
- **Documentation**: Auto-generated API docs with Swagger/ReDoc

## Extension Points

### Adding New Agent Types
1. Create enum entry in `AgentIdentifier`
2. Implement `AgentWorkflow` subclass
3. Add template files in `app/agents/templates/`
4. Register in workflow factory
5. Update database seeds

### Adding New Integrations
1. Add provider to `IntegrationProvider` enum
2. Implement OAuth client in `app/integrations/oauth/`
3. Create client in `app/integrations/clients/`
4. Add capability mappings
5. Update frontend integration components

### Custom MCP Servers
1. Implement MCP protocol
2. Configure in session MCP configs
3. Add server-specific templates
4. Test with agent workflows

This technical documentation provides the complete architectural foundation needed to understand, maintain, and extend the Optima AI system.
