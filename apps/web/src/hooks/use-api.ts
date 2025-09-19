import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
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
  DashboardStats,
  Workflow,
  Integration,
  PaginationParams
} from '@/types/api';
import { apiClient, handleApiError } from '@/lib/api';
import { toast } from 'sonner';

// Query keys for caching
export const queryKeys = {
  auth: {
    user: ['auth', 'user'] as const,
  },
  agents: {
    all: ['agents'] as const,
    list: (params?: any) => ['agents', 'list', params] as const,
    detail: (id: number) => ['agents', 'detail', id] as const,
  },
  projects: {
    all: ['projects'] as const,
    list: (params?: any) => ['projects', 'list', params] as const,
    detail: (id: number) => ['projects', 'detail', id] as const,
  },
  workflows: {
    all: ['workflows'] as const,
    list: (params?: any) => ['workflows', 'list', params] as const,
    detail: (id: number) => ['workflows', 'detail', id] as const,
  },
  integrations: {
    all: ['integrations'] as const,
    list: (params?: any) => ['integrations', 'list', params] as const,
    detail: (id: number) => ['integrations', 'detail', id] as const,
  },
  dashboard: {
    stats: ['dashboard', 'stats'] as const,
  },
} as const;

// Authentication hooks
export const useCurrentUser = (options?: UseQueryOptions<User>) => {
  return useQuery({
    queryKey: queryKeys.auth.user,
    queryFn: () => apiClient.getCurrentUser(),
    enabled: apiClient.isAuthenticated(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
};

export const useLogin = (options?: UseMutationOptions<AuthResponse, Error, LoginRequest>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (credentials: LoginRequest) => apiClient.login(credentials),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.auth.user, data.user);
      toast.success('Login successful');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useRegister = (options?: UseMutationOptions<AuthResponse, Error, RegisterRequest>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: RegisterRequest) => apiClient.register(userData),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.auth.user, data.user);
      toast.success('Registration successful');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useLogout = (options?: UseMutationOptions<void, Error, void>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => apiClient.logout(),
    onSuccess: () => {
      queryClient.clear();
      toast.success('Logged out successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

// Agent hooks
export const useAgents = (
  params?: PaginationParams & { project_id?: number; agent_type?: string },
  options?: UseQueryOptions<AgentListResponse>
) => {
  return useQuery({
    queryKey: queryKeys.agents.list(params),
    queryFn: () => apiClient.getAgents(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useAgent = (id: number, options?: UseQueryOptions<Agent>) => {
  return useQuery({
    queryKey: queryKeys.agents.detail(id),
    queryFn: () => apiClient.getAgent(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useCreateAgent = (options?: UseMutationOptions<Agent, Error, AgentCreate>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (agent: AgentCreate) => apiClient.createAgent(agent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.all });
      toast.success('Agent created successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useUpdateAgent = (options?: UseMutationOptions<Agent, Error, { id: number; agent: AgentUpdate }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, agent }: { id: number; agent: AgentUpdate }) => apiClient.updateAgent(id, agent),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.agents.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.all });
      toast.success('Agent updated successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useDeleteAgent = (options?: UseMutationOptions<void, Error, number>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteAgent(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.agents.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.all });
      toast.success('Agent deleted successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useExecuteAgent = (options?: UseMutationOptions<{ message: string }, Error, number>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.executeAgent(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats });
      toast.success(data.message);
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

// Project hooks
export const useProjects = (
  params?: PaginationParams,
  options?: UseQueryOptions<Project[]>
) => {
  return useQuery({
    queryKey: queryKeys.projects.list(params),
    queryFn: () => apiClient.getProjects(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useProject = (id: number, options?: UseQueryOptions<Project>) => {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => apiClient.getProject(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useCreateProject = (options?: UseMutationOptions<Project, Error, ProjectCreate>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (project: ProjectCreate) => apiClient.createProject(project),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Project created successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useUpdateProject = (options?: UseMutationOptions<Project, Error, { id: number; project: ProjectUpdate }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, project }: { id: number; project: ProjectUpdate }) => apiClient.updateProject(id, project),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.projects.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Project updated successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

export const useDeleteProject = (options?: UseMutationOptions<void, Error, number>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiClient.deleteProject(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.projects.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Project deleted successfully');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
    ...options,
  });
};

// Workflow hooks
export const useWorkflows = (
  params?: PaginationParams,
  options?: UseQueryOptions<Workflow[]>
) => {
  return useQuery({
    queryKey: queryKeys.workflows.list(params),
    queryFn: () => apiClient.getWorkflows(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useWorkflow = (id: number, options?: UseQueryOptions<Workflow>) => {
  return useQuery({
    queryKey: queryKeys.workflows.detail(id),
    queryFn: () => apiClient.getWorkflow(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

// Integration hooks
export const useIntegrations = (
  params?: PaginationParams,
  options?: UseQueryOptions<Integration[]>
) => {
  return useQuery({
    queryKey: queryKeys.integrations.list(params),
    queryFn: () => apiClient.getIntegrations(params),
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

export const useIntegration = (id: number, options?: UseQueryOptions<Integration>) => {
  return useQuery({
    queryKey: queryKeys.integrations.detail(id),
    queryFn: () => apiClient.getIntegration(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options,
  });
};

// Dashboard hooks
export const useDashboardStats = (options?: UseQueryOptions<DashboardStats>) => {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: () => apiClient.getDashboardStats(),
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 60, // Refetch every minute
    ...options,
  });
};
