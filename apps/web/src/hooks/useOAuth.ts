import { useOAuthStore } from '@/store/oauth';

/**
 * Custom hook for managing OAuth connection states
 *
 */
export const useOAuth = () => {
  const {
    notionConnection,
    gitHubConnection,
    atlassianMCPConnection,
    figmaConnection,
    setAtlassianMCPConnection,
    setNotionConnection,
    setGitHubConnection,
    setFigmaConnection,
    resetConnections,
    resetNotionConnection,
    resetGitHubConnection,
    resetAtlassianMCPConnection,
    resetFigmaConnection,
  } = useOAuthStore();

  return {
    notionConnection,
    gitHubConnection,
    atlassianMCPConnection,
    figmaConnection,
    setAtlassianMCPConnection,
    setNotionConnection,
    setGitHubConnection,
    setFigmaConnection,
    resetConnections,
    resetNotionConnection,
    resetGitHubConnection,
    resetAtlassianMCPConnection,
    resetFigmaConnection,
  };
};
