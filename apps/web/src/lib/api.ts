import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  Agent, 
  AgentCreate, 
  AgentUpdate, 
  AgentListResponse,
  Project,
  ProjectCreate,
  ProjectUpdate,
  User,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshRequest,
  DashboardStats,
  Workflow,
  Integration,
  PaginationParams
} from '@/types/api';

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          if (this.refreshToken) {
            try {
              const response = await this.refreshAccessToken();
              this.setTokens(response.access_token, response.refresh_token);
              originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              return this.client(originalRequest);
            } catch (refreshError) {
              this.clearTokens();
              window.location.href = '/auth/login';
              return Promise.reject(refreshError);
            }
          } else {
            this.clearTokens();
            window.location.href = '/auth/login';
          }
        }

        return Promise.reject(error);
      }
    );

    // Initialize tokens from localStorage if available
    this.initializeTokens();
  }

  private initializeTokens() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  public setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  public clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  public isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', credentials);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', userData);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async refreshAccessToken(): Promise<AuthResponse> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.client.post<AuthResponse>('/auth/refresh', {
      refresh_token: this.refreshToken,
    });
    
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Agent endpoints
  async getAgents(params?: PaginationParams & {
    project_id?: number;
    agent_type?: string;
  }): Promise<AgentListResponse> {
    const response = await this.client.get<AgentListResponse>('/agents', { params });
    return response.data;
  }

  async getAgent(id: number): Promise<Agent> {
    const response = await this.client.get<Agent>(`/agents/${id}`);
    return response.data;
  }

  async createAgent(agent: AgentCreate): Promise<Agent> {
    const response = await this.client.post<Agent>('/agents', agent);
    return response.data;
  }

  async updateAgent(id: number, agent: AgentUpdate): Promise<Agent> {
    const response = await this.client.put<Agent>(`/agents/${id}`, agent);
    return response.data;
  }

  async deleteAgent(id: number): Promise<void> {
    await this.client.delete(`/agents/${id}`);
  }

  async executeAgent(id: number): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>(`/agents/${id}/execute`);
    return response.data;
  }

  // Project endpoints
  async getProjects(params?: PaginationParams): Promise<Project[]> {
    const response = await this.client.get<Project[]>('/projects', { params });
    return response.data;
  }

  async getProject(id: number): Promise<Project> {
    const response = await this.client.get<Project>(`/projects/${id}`);
    return response.data;
  }

  async createProject(project: ProjectCreate): Promise<Project> {
    const response = await this.client.post<Project>('/projects', project);
    return response.data;
  }

  async updateProject(id: number, project: ProjectUpdate): Promise<Project> {
    const response = await this.client.put<Project>(`/projects/${id}`, project);
    return response.data;
  }

  async deleteProject(id: number): Promise<void> {
    await this.client.delete(`/projects/${id}`);
  }

  // Workflow endpoints
  async getWorkflows(params?: PaginationParams): Promise<Workflow[]> {
    const response = await this.client.get<Workflow[]>('/workflows', { params });
    return response.data;
  }

  async getWorkflow(id: number): Promise<Workflow> {
    const response = await this.client.get<Workflow>(`/workflows/${id}`);
    return response.data;
  }

  // Integration endpoints
  async getIntegrations(params?: PaginationParams): Promise<Integration[]> {
    const response = await this.client.get<Integration[]>('/integrations', { params });
    return response.data;
  }

  async getIntegration(id: number): Promise<Integration> {
    const response = await this.client.get<Integration>(`/integrations/${id}`);
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/dashboard/stats');
    return response.data;
  }

  async getDashboardActivity(limit?: number): Promise<any[]> {
    const response = await this.client.get<any[]>('/dashboard/activity', {
      params: { limit },
    });
    return response.data;
  }

  async getDashboardMetrics(timeframe?: string): Promise<any> {
    const response = await this.client.get('/dashboard/metrics', {
      params: { timeframe },
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };

// Utility function for handling API errors
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      // Validation errors
      return error.response.data.detail
        .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
        .join(', ');
    }
    return error.response.data.detail;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};
