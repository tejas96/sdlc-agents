'use client';

import { useState } from 'react';
import {
  ConfluenceIcon,
  NotionIcon,
  GitIcon,
  GitLabIcon,
  LinearIcon,
  MSTeamsIcon,
  SlackIcon,
  ServiceNowIcon,
  GoogleDriveIcon,
} from '@/components/icons';
import { ServiceTile } from '@/components/features/settings/ServiceTile';
import { GitHubModal } from '@/components/shared/GitHubModal';
import { FigmaModal } from '@/components/shared/FigmaModal';
import { useOAuth } from '@/hooks/useOAuth';
import { useUser } from '@/hooks/useUser';
import { integrationApi } from '@/lib/api/api';
import { toast } from 'sonner';

import { useOAuthTokenHandler } from '@/hooks/useOAuthTokenHandler';

// Service configuration constants
const SERVICES = [
  {
    id: 'notion',
    title: 'Notion',
    icon: NotionIcon,
    connectedDescription: 'Connected',
    disconnectedDescription: 'Connect with OAuth',
    type: 'oauth',
    oauthProvider: 'notion',
  },
  {
    id: 'atlassian',
    title: 'Atlassian',
    icon: ConfluenceIcon,
    connectedDescription: 'Connected via MCP',
    disconnectedDescription: 'Connect with MCP OAuth',
    type: 'oauth',
    oauthProvider: 'atlassian-mcp',
  },
  {
    id: 'github',
    title: 'GitHub',
    icon: GitIcon,
    connectedDescription: 'Connected',
    disconnectedDescription: 'Enter API token',
    type: 'token',
  },
  // {
  //   id: 'figma',
  //   title: 'Figma',
  //   icon: FigmaIcon,
  //   connectedDescription: 'Connected',
  //   disconnectedDescription: 'Enter API token',
  //   type: 'token',
  // },
  {
    id: 'gitlab',
    title: 'GitLab',
    icon: GitLabIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'token',
    comingSoon: true,
  },
  {
    id: 'linear',
    title: 'Linear',
    icon: LinearIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'oauth',
    comingSoon: true,
  },
  {
    id: 'msteams',
    title: 'Microsoft Teams',
    icon: MSTeamsIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'oauth',
    comingSoon: true,
  },
  {
    id: 'slack',
    title: 'Slack',
    icon: SlackIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'oauth',
    comingSoon: true,
  },
  {
    id: 'servicenow',
    title: 'ServiceNow',
    icon: ServiceNowIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'oauth',
    comingSoon: true,
  },
  {
    id: 'googledrive',
    title: 'Google Drive',
    icon: GoogleDriveIcon,
    connectedDescription: 'Coming Soon',
    disconnectedDescription: 'Coming Soon',
    type: 'oauth',
    comingSoon: true,
  },
] as const;

export default function SettingsPage() {
  const {
    notionConnection,
    gitHubConnection,
    figmaConnection,
    atlassianMCPConnection,
    setAtlassianMCPConnection,
    setNotionConnection,
    setGitHubConnection,
    setFigmaConnection,
  } = useOAuth();
  const { accessToken } = useUser();
  const [showGitHubModal, setShowGitHubModal] = useState(false);
  const [showFigmaModal, setShowFigmaModal] = useState(false);

  // useOAuthTokenHandler
  useOAuthTokenHandler();

  const getConnectionStatus = (serviceId: string) => {
    switch (serviceId) {
      case 'notion':
        return notionConnection;
      case 'atlassian':
        return atlassianMCPConnection;
      case 'github':
        return gitHubConnection;
      case 'figma':
        return figmaConnection;
      default:
        return { isConnected: false, id: 0 };
    }
  };

  // Handle OAuth service clicks
  const handleOAuthClick = (provider: string) => {
    window.location.href = `/api/auth/${provider}?from=${window.location.href}`;
  };

  // Handle token service clicks
  const handleTokenClick = (serviceId: string) => {
    switch (serviceId) {
      case 'github':
        setShowGitHubModal(true);
        break;
      case 'figma':
        setShowFigmaModal(true);
        break;
      default:
        break;
    }
  };

  // Handle service disconnect
  const handleDisconnect = async (serviceId: string) => {
    const connectionStatus = getConnectionStatus(serviceId);
    if (!connectionStatus.isConnected || !connectionStatus.id || !accessToken) {
      return;
    }

    try {
      const response = await integrationApi.delete(
        connectionStatus.id,
        accessToken
      );

      if (response.success) {
        // Reset the connection state based on service type
        switch (serviceId) {
          case 'notion':
            setNotionConnection({
              isConnected: false,
              id: 0,
            });
            toast.success('Notion disconnected successfully');
            break;
          case 'atlassian':
            setAtlassianMCPConnection({
              isConnected: false,
              id: 0,
            });
            toast.success('Atlassian MCP disconnected successfully');
            break;
          case 'github':
            setGitHubConnection({
              isConnected: false,
              id: 0,
            });
            toast.success('GitHub disconnected successfully');
            break;
          case 'figma':
            setFigmaConnection({
              isConnected: false,
              id: 0,
            });
            toast.success('Figma disconnected successfully');
            break;
        }
      } else {
        toast.error(
          `Failed to disconnect ${serviceId}: ${response.error || response.message || 'Unknown error'}`
        );
      }
    } catch {
      toast.error(`Failed to disconnect ${serviceId}. Please try again.`);
    }
  };

  return (
    <div className='space-y-8'>
      <div>
        <div className='mb-6'>
          <h1 className='mb-2 text-2xl font-bold'>Integrations</h1>
          <p className='text-muted-foreground'>
            Connect your favorite tools and services to enhance your workflow
          </p>
        </div>

        {/* All Integrations */}
        <div className='flex flex-wrap gap-4'>
          {SERVICES.map(service => {
            const connectionStatus = getConnectionStatus(service.id);
            return (
              <ServiceTile
                key={service.id}
                icon={service.icon}
                title={service.title}
                isConnected={connectionStatus.isConnected}
                description={
                  connectionStatus.isConnected
                    ? service.connectedDescription
                    : service.disconnectedDescription
                }
                onClick={() => {
                  if ('comingSoon' in service && service.comingSoon) return;
                  if (service.type === 'oauth' && 'oauthProvider' in service) {
                    handleOAuthClick(service.oauthProvider);
                  } else if (service.type === 'token') {
                    handleTokenClick(service.id);
                  }
                }}
                onDisconnect={() => handleDisconnect(service.id)}
                disabled={'comingSoon' in service && service.comingSoon}
              />
            );
          })}
        </div>
      </div>

      <GitHubModal open={showGitHubModal} onOpenChange={setShowGitHubModal} />
      <FigmaModal open={showFigmaModal} onOpenChange={setShowFigmaModal} />
    </div>
  );
}
