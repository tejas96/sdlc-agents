import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  RepositoryState,
  AtlassianIssue,
  AtlassianPage,
  AtlassianProject,
  AtlassianSpace,
  NotionPage,
  FigmaFile,
} from '@/types';

type OutputConfigType = {
  type: string;
  contents: string[];
};
interface ProjectState {
  projectName: string;
  analysisType: string;
  aiEngine: string;
  mcpAgents: string[];
  contentsToInclude: string[];
  userPrompt: string;
  agentType: string;
  sessionId: string;
  output_config_type: string[];
  output_config_content: string[];
  output: OutputConfigType[];
  prdnotion: {
    pages: NotionPage[];
    selectedPages: { id: string; url: string }[];
  };
  prdconfluence: {
    pages: AtlassianPage[];
    selectedPages: string[];
  };
  prdjira: {
    tickets: AtlassianIssue[];
    selectedTickets: string[];
  };
  docsnotion: {
    pages: NotionPage[];
    selectedPages: { id: string; url: string }[];
  };
  docsconfluence: {
    pages: AtlassianPage[];
    selectedPages: string[];
  };
  docsjira: {
    tickets: AtlassianIssue[];
    selectedTickets: string[];
  };
  prdfigma: {
    files: FigmaFile[];
    selectedFiles: string[];
  };
  docsfigma: {
    files: FigmaFile[];
    selectedFiles: string[];
  };
  cachedNotionPages: NotionPage[];
  cachedConfluenceSpaces: AtlassianSpace[];
  cachedConfluencePages: AtlassianPage[];
  cachedJiraProjects: AtlassianProject[];
  cachedJiraTickets: AtlassianIssue[];
  gitHubRepos: {
    repositories: RepositoryState[];
    selectedRepositories: {
      url: string;
      branch: string;
    }[];
    selectedPR?: {
      html_url: string;
    } | null;
  };
  setPrdnotion: (prdnotion: {
    pages: NotionPage[];
    selectedPages: { id: string; url: string }[];
  }) => void;
  setPrdconfluence: (prdconfluence: {
    pages: AtlassianPage[];
    selectedPages: string[];
  }) => void;
  setPrdjira: (prdjira: {
    tickets: AtlassianIssue[];
    selectedTickets: string[];
  }) => void;
  setDocsnotion: (docsnotion: {
    pages: NotionPage[];
    selectedPages: { id: string; url: string }[];
  }) => void;
  setDocsconfluence: (docsconfluence: {
    pages: AtlassianPage[];
    selectedPages: string[];
  }) => void;
  setDocsjira: (docsjira: {
    tickets: AtlassianIssue[];
    selectedTickets: string[];
  }) => void;
  setPrdfigma: (prdfigma: {
    files: FigmaFile[];
    selectedFiles: string[];
  }) => void;
  setDocsfigma: (docsfigma: {
    files: FigmaFile[];
    selectedFiles: string[];
  }) => void;
  setCachedNotionPages: (cachedNotionPages: NotionPage[]) => void;
  setCachedConfluenceSpaces: (cachedConfluenceSpaces: AtlassianSpace[]) => void;
  setCachedConfluencePages: (cachedConfluencePages: AtlassianPage[]) => void;
  setCachedJiraProjects: (cachedJiraProjects: AtlassianProject[]) => void;
  setCachedJiraTickets: (cachedJiraTickets: AtlassianIssue[]) => void;
  setGitHubRepos: (gitHubRepos: {
    repositories: RepositoryState[];
    selectedRepositories: {
      url: string;
      branch: string;
    }[];
    selectedPR?: {
      html_url: string;
    } | null;
  }) => void;
  setSelectedPR: (
    pr: {
      html_url: string;
    } | null
  ) => void;
  setOutputConfigType: (output_config_type: string[]) => void;
  setOutputConfigContent: (output_config_content: string[]) => void;
  setOutput: (output: OutputConfigType[]) => void;
  setSessionId: (sessionId: string) => void;
  setAgentType: (agentType: string) => void;
  setUserPrompt: (userPrompt: string) => void;
  setContentsToInclude: (contentsToInclude: string[]) => void;
  setMcpAgents: (mcpAgents: string[]) => void;
  setAiEngine: (aiEngine: string) => void;
  setAnalysisType: (analysisType: string) => void;
  setProjectName: (projectName: string) => void;
  resetProject: () => void;
  resetGitHubRepos: () => void;
  resetPrdnotion: () => void;
  resetPrdconfluence: () => void;
  resetPrdjira: () => void;
  resetDocsnotion: () => void;
  resetDocsconfluence: () => void;
  resetDocsjira: () => void;
  resetPrdfigma: () => void;
  resetDocsfigma: () => void;
  resetCachedNotionPages: () => void;
  resetCachedConfluenceSpaces: () => void;
  resetCachedConfluencePages: () => void;
  resetCachedJiraProjects: () => void;
  resetCachedJiraTickets: () => void;
  resetOutputConfigType: () => void;
  resetOutputConfigContent: () => void;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    persist(
      set => ({
        projectName: '',
        analysisType: 'deep',
        aiEngine: 'claude-4-sonnet',
        mcpAgents: [],
        contentsToInclude: [],
        userPrompt: '',
        agentType: '',
        prdnotion: {
          pages: [],
          selectedPages: [],
        },
        prdconfluence: {
          pages: [],
          selectedPages: [],
        },
        prdjira: {
          tickets: [],
          selectedTickets: [],
        },
        docsnotion: {
          pages: [],
          selectedPages: [],
        },
        docsconfluence: {
          pages: [],
          selectedPages: [],
        },
        docsjira: {
          tickets: [],
          selectedTickets: [],
        },
        prdfigma: {
          files: [],
          selectedFiles: [],
        },
        docsfigma: {
          files: [],
          selectedFiles: [],
        },
        cachedNotionPages: [],
        cachedConfluenceSpaces: [],
        cachedConfluencePages: [],
        cachedJiraProjects: [],
        cachedJiraTickets: [],
        gitHubRepos: {
          repositories: [],
          selectedRepositories: [],
          selectedPR: null,
        },
        sessionId: '',
        output_config_type: [],
        output_config_content: [],
        output: [],
        setSessionId: (sessionId: string) => set(() => ({ sessionId })),
        setAgentType: (agentType: string) => set(() => ({ agentType })),
        setUserPrompt: (userPrompt: string) => set(() => ({ userPrompt })),
        setProjectName: (projectName: string) => set(() => ({ projectName })),
        setAnalysisType: (analysisType: string) =>
          set(() => ({ analysisType })),
        setAiEngine: (aiEngine: string) => set(() => ({ aiEngine })),
        setMcpAgents: (mcpAgents: string[]) => set(() => ({ mcpAgents })),
        setContentsToInclude: (contentsToInclude: string[]) =>
          set(() => ({ contentsToInclude })),
        setPrdnotion: (prdnotion: {
          pages: NotionPage[];
          selectedPages: { id: string; url: string }[];
        }) => set(() => ({ prdnotion })),
        setPrdconfluence: (prdconfluence: {
          pages: AtlassianPage[];
          selectedPages: string[];
        }) => set(() => ({ prdconfluence })),
        setPrdjira: (prdjira: {
          tickets: AtlassianIssue[];
          selectedTickets: string[];
        }) => set(() => ({ prdjira })),
        setDocsnotion: (docsnotion: {
          pages: NotionPage[];
          selectedPages: { id: string; url: string }[];
        }) => set(() => ({ docsnotion })),
        setDocsconfluence: (docsconfluence: {
          pages: AtlassianPage[];
          selectedPages: string[];
        }) => set(() => ({ docsconfluence })),
        setDocsjira: (docsjira: {
          tickets: AtlassianIssue[];
          selectedTickets: string[];
        }) => set(() => ({ docsjira })),
        setPrdfigma: (prdfigma: {
          files: FigmaFile[];
          selectedFiles: string[];
        }) => set(() => ({ prdfigma })),
        setDocsfigma: (docsfigma: {
          files: FigmaFile[];
          selectedFiles: string[];
        }) => set(() => ({ docsfigma })),
        setCachedNotionPages: (cachedNotionPages: NotionPage[]) =>
          set(() => ({ cachedNotionPages })),
        setCachedConfluenceSpaces: (cachedConfluenceSpaces: AtlassianSpace[]) =>
          set(() => ({ cachedConfluenceSpaces })),
        setCachedConfluencePages: (cachedConfluencePages: AtlassianPage[]) =>
          set(() => ({ cachedConfluencePages })),
        setCachedJiraProjects: (cachedJiraProjects: AtlassianProject[]) =>
          set(() => ({ cachedJiraProjects })),
        setCachedJiraTickets: (cachedJiraTickets: AtlassianIssue[]) =>
          set(() => ({ cachedJiraTickets })),
        setGitHubRepos: (gitHubRepos: {
          repositories: RepositoryState[];
          selectedRepositories: {
            url: string;
            branch: string;
          }[];
          selectedPR?: {
            html_url: string;
          } | null;
        }) => set(() => ({ gitHubRepos })),
        setSelectedPR: (
          selectedPR: {
            html_url: string;
          } | null
        ) =>
          set(state => ({
            gitHubRepos: {
              ...state.gitHubRepos,
              selectedPR,
            },
          })),
        setOutputConfigType: (output_config_type: string[]) =>
          set(() => ({ output_config_type })),
        setOutputConfigContent: (output_config_content: string[]) =>
          set(() => ({ output_config_content })),
        setOutput: (output: OutputConfigType[]) => set(() => ({ output })),
        resetProject: () =>
          set(() => ({
            projectName: '',
            analysisType: 'deep',
            aiEngine: 'claude-4-sonnet',
            mcpAgents: [],
            contentsToInclude: [],
            userPrompt: '',
            agentType: '',
            sessionId: '',
            prdnotion: {
              pages: [],
              selectedPages: [],
            },
            prdconfluence: {
              pages: [],
              selectedPages: [],
            },
            prdjira: {
              tickets: [],
              selectedTickets: [],
            },
            docsnotion: {
              pages: [],
              selectedPages: [],
            },
            docsconfluence: {
              pages: [],
              selectedPages: [],
            },
            docsjira: {
              tickets: [],
              selectedTickets: [],
            },
            prdfigma: {
              files: [],
              selectedFiles: [],
            },
            docsfigma: {
              files: [],
              selectedFiles: [],
            },
            cachedNotionPages: [],
            cachedConfluenceSpaces: [],
            cachedConfluencePages: [],
            cachedJiraProjects: [],
            cachedJiraTickets: [],
            gitHubRepos: {
              repositories: [],
              selectedRepositories: [],
              selectedPR: null,
            },
            output_config_type: [],
            output_config_content: [],
            output: [],
          })),
        resetGitHubRepos: () =>
          set(() => ({
            gitHubRepos: {
              repositories: [],
              selectedRepositories: [],
              selectedPR: null,
            },
          })),
        resetPrdnotion: () =>
          set(() => ({
            prdnotion: {
              pages: [],
              selectedPages: [],
            },
          })),
        resetPrdconfluence: () =>
          set(() => ({
            prdconfluence: {
              pages: [],
              selectedPages: [],
            },
          })),
        resetPrdjira: () =>
          set(() => ({
            prdjira: {
              tickets: [],
              selectedTickets: [],
            },
          })),
        resetDocsnotion: () =>
          set(() => ({
            docsnotion: {
              pages: [],
              selectedPages: [],
            },
          })),
        resetDocsconfluence: () =>
          set(() => ({
            docsconfluence: {
              pages: [],
              selectedPages: [],
            },
          })),
        resetDocsjira: () =>
          set(() => ({
            docsjira: {
              tickets: [],
              selectedTickets: [],
            },
          })),
        resetPrdfigma: () =>
          set(() => ({
            prdfigma: {
              files: [],
              selectedFiles: [],
            },
          })),
        resetDocsfigma: () =>
          set(() => ({
            docsfigma: {
              files: [],
              selectedFiles: [],
            },
          })),
        resetCachedNotionPages: () => set(() => ({ cachedNotionPages: [] })),
        resetCachedConfluenceSpaces: () =>
          set(() => ({ cachedConfluenceSpaces: [] })),
        resetCachedConfluencePages: () =>
          set(() => ({ cachedConfluencePages: [] })),
        resetCachedJiraProjects: () => set(() => ({ cachedJiraProjects: [] })),
        resetCachedJiraTickets: () => set(() => ({ cachedJiraTickets: [] })),
        resetOutputConfigType: () => set(() => ({ output_config_type: [] })),
        resetOutputConfigContent: () =>
          set(() => ({ output_config_content: [] })),
      }),
      {
        name: 'project-storage',
      }
    ),
    {
      name: 'project-store',
    }
  )
);
