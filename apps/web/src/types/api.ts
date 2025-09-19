// API Types for SDLC Agents
// Based on the backend models and schemas

export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: number;
  name: string;
  slug: string;
  description?: string;
  agent_type: AgentType;
  status: AgentStatus;
  config?: string;
  prompt_template?: string;
  model_name: string;
  max_tokens: number;
  temperature: number;
  timeout_seconds: number;
  schedule_cron?: string;
  trigger_events?: string;
  total_executions: number;
  successful_executions: number;
  last_execution_at?: string;
  project_id?: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

export enum AgentType {
  CODE_REVIEWER = "code_reviewer",
  TEST_GENERATOR = "test_generator", 
  DOCUMENTATION_WRITER = "documentation_writer",
  BUG_HUNTER = "bug_hunter",
  PERFORMANCE_OPTIMIZER = "performance_optimizer",
  SECURITY_SCANNER = "security_scanner",
  DEPLOYMENT_MANAGER = "deployment_manager",
  MONITORING_AGENT = "monitoring_agent",
  CUSTOM = "custom"
}

export enum AgentStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  PAUSED = "paused",
  ERROR = "error",
  MAINTENANCE = "maintenance"
}

export interface Project {
  id: number;
  name: string;
  slug: string;
  description?: string;
  status: ProjectStatus;
  project_type: ProjectType;
  repository_url?: string;
  repository_branch: string;
  local_path?: string;
  tech_stack?: string;
  tags?: string;
  environment_config?: string;
  build_config?: string;
  deployment_config?: string;
  jira_project_key?: string;
  slack_channel_id?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

export enum ProjectStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  ARCHIVED = "archived",
  COMPLETED = "completed"
}

export enum ProjectType {
  WEB_APP = "web_app",
  MOBILE_APP = "mobile_app",
  DESKTOP_APP = "desktop_app",
  LIBRARY = "library",
  API = "api",
  MICROSERVICE = "microservice",
  DATA_PIPELINE = "data_pipeline",
  ML_PROJECT = "ml_project",
  OTHER = "other"
}

export interface Workflow {
  id: number;
  name: string;
  slug: string;
  description?: string;
  workflow_type: string;
  status: string;
  config?: string;
  schedule_cron?: string;
  trigger_events?: string;
  total_executions: number;
  successful_executions: number;
  last_execution_at?: string;
  project_id?: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

export interface Integration {
  id: number;
  name: string;
  provider: string;
  config?: string;
  is_active: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

// API Request/Response types
export interface AgentListResponse {
  agents: Agent[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export type AgentResponse = Agent;

export interface AgentCreate {
  name: string;
  slug: string;
  description?: string;
  agent_type: AgentType;
  status?: AgentStatus;
  config?: string;
  prompt_template?: string;
  model_name?: string;
  max_tokens?: number;
  temperature?: number;
  timeout_seconds?: number;
  schedule_cron?: string;
  trigger_events?: string;
  project_id?: number;
}

export interface AgentUpdate {
  name?: string;
  slug?: string;
  description?: string;
  agent_type?: AgentType;
  status?: AgentStatus;
  config?: string;
  prompt_template?: string;
  model_name?: string;
  max_tokens?: number;
  temperature?: number;
  timeout_seconds?: number;
  schedule_cron?: string;
  trigger_events?: string;
  project_id?: number;
}

export interface ProjectCreate {
  name: string;
  slug: string;
  description?: string;
  status?: ProjectStatus;
  project_type?: ProjectType;
  repository_url?: string;
  repository_branch?: string;
  local_path?: string;
  tech_stack?: string;
  tags?: string;
  environment_config?: string;
  build_config?: string;
  deployment_config?: string;
  jira_project_key?: string;
  slack_channel_id?: string;
}

export interface ProjectUpdate {
  name?: string;
  slug?: string;
  description?: string;
  status?: ProjectStatus;
  project_type?: ProjectType;
  repository_url?: string;
  repository_branch?: string;
  local_path?: string;
  tech_stack?: string;
  tags?: string;
  environment_config?: string;
  build_config?: string;
  deployment_config?: string;
  jira_project_key?: string;
  slack_channel_id?: string;
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshRequest {
  refresh_token: string;
}

// API Error types
export interface ApiError {
  detail: string;
  status_code: number;
}

export interface ValidationError {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}

// Pagination types
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Dashboard statistics
export interface DashboardStats {
  active_agents: number;
  total_projects: number;
  tasks_completed: number;
  avg_response_time: string;
  system_uptime: string;
  recent_activity: Activity[];
}

export interface Activity {
  id: number;
  type: 'agent_execution' | 'project_created' | 'workflow_completed';
  title: string;
  description: string;
  timestamp: string;
  agent_id?: number;
  project_id?: number;
  workflow_id?: number;
}

// Chart data types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}
