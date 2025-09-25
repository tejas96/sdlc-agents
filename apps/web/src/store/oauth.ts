import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface OAuthState {
  notionConnection: {
    isConnected: boolean;
    id: number;
  };
  gitHubConnection: {
    isConnected: boolean;
    id: number;
  };
  atlassianMCPConnection: {
    isConnected: boolean;
    id: number;
  };
  figmaConnection: {
    isConnected: boolean;
    id: number;
  };
  setNotionConnection: (connection: {
    isConnected: boolean;
    id: number;
  }) => void;
  setGitHubConnection: (connection: {
    isConnected: boolean;
    id: number;
  }) => void;
  setAtlassianMCPConnection: (connection: {
    isConnected: boolean;
    id: number;
  }) => void;
  setFigmaConnection: (connection: {
    isConnected: boolean;
    id: number;
  }) => void;
  resetConnections: () => void;
  resetNotionConnection: () => void;
  resetGitHubConnection: () => void;
  resetAtlassianMCPConnection: () => void;
  resetFigmaConnection: () => void;
}

export const useOAuthStore = create<OAuthState>()(
  devtools(
    persist(
      set => ({
        notionConnection: {
          isConnected: false,
          id: 0,
        },
        gitHubConnection: {
          isConnected: false,
          id: 0,
        },
        atlassianMCPConnection: {
          isConnected: false,
          id: 0,
        },
        figmaConnection: {
          isConnected: false,
          id: 0,
        },
        setGitHubConnection: (connection: {
          isConnected: boolean;
          id: number;
        }) => set(() => ({ gitHubConnection: connection })),
        setNotionConnection: (connection: {
          isConnected: boolean;
          id: number;
        }) => set(() => ({ notionConnection: connection })),
        setAtlassianMCPConnection: (connection: {
          isConnected: boolean;
          id: number;
        }) => set(() => ({ atlassianMCPConnection: connection })),
        setFigmaConnection: (connection: {
          isConnected: boolean;
          id: number;
        }) => set(() => ({ figmaConnection: connection })),
        resetNotionConnection: () =>
          set(() => ({
            notionConnection: {
              isConnected: false,
              id: 0,
            },
          })),
        resetGitHubConnection: () =>
          set(() => ({
            gitHubConnection: {
              isConnected: false,
              id: 0,
            },
          })),
        resetAtlassianMCPConnection: () =>
          set(() => ({
            atlassianMCPConnection: {
              isConnected: false,
              id: 0,
            },
          })),
        resetFigmaConnection: () =>
          set(() => ({
            figmaConnection: {
              isConnected: false,
              id: 0,
            },
          })),
        resetConnections: () =>
          set(() => ({
            notionConnection: {
              isConnected: false,
              id: 0,
            },
            gitHubConnection: {
              isConnected: false,
              id: 0,
            },
            atlassianMCPConnection: {
              isConnected: false,
              id: 0,
            },
            figmaConnection: {
              isConnected: false,
              id: 0,
            },
          })),
      }),
      {
        name: 'oauth-store',
      }
    ),
    {
      name: 'oauth-store',
    }
  )
);

export const resetOAuthStore = () =>
  useOAuthStore.getState().resetConnections();
