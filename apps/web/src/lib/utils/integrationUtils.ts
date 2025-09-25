type DocumentType = 'prd' | 'supporting_doc';

export interface AvailableIntegrations {
  notion: boolean;
  confluence: boolean;
  jira: boolean;
  figma: boolean;
}

// Integration data structure from API
interface Integration {
  id: number;
  type: string;
  is_active: boolean;
}

// Connection state structure
interface ConnectionState {
  isConnected: boolean;
  id: number;
}

// Setter functions for each integration type
interface IntegrationSetters {
  setNotionConnection: (state: ConnectionState) => void;
  setAtlassianMCPConnection: (state: ConnectionState) => void;
  setGitHubConnection: (state: ConnectionState) => void;
  setFigmaConnection: (state: ConnectionState) => void;
}

/**
 * Determine which integrations to show based on agent type and document type
 */
export function getAvailableIntegrations(
  agentType: string = 'default',
  documentType: DocumentType
): AvailableIntegrations {
  switch (agentType) {
    case 'test_case_generation':
      switch (documentType) {
        case 'prd':
          return {
            notion: true,
            confluence: true,
            jira: true,
            figma: false,
          };
        case 'supporting_doc':
          return {
            notion: true,
            confluence: true,
            jira: false,
            figma: false,
          };
        default:
          return { notion: true, confluence: true, jira: true, figma: true };
      }

    case 'code_analysis':
      switch (documentType) {
        case 'supporting_doc':
          return {
            notion: true,
            confluence: true,
            jira: false,
            figma: false,
          };
        default:
          return { notion: true, confluence: true, jira: true, figma: false };
      }

    case 'requirements_to_tickets':
      switch (documentType) {
        case 'prd':
          return {
            notion: true,
            confluence: true,
            jira: true,
            figma: false,
          };
        case 'supporting_doc':
          return {
            notion: true,
            confluence: true,
            jira: false,
            figma: false,
          };
        default:
          return { notion: true, confluence: true, jira: true, figma: false };
      }
    case 'code_reviewer':
      switch (documentType) {
        case 'prd':
          return {
            notion: false,
            confluence: false,
            jira: false,
            figma: false,
          };
        case 'supporting_doc':
          return {
            notion: true,
            confluence: true,
            jira: false,
            figma: false,
          };
        default:
          return { notion: true, confluence: true, jira: true, figma: false };
      }

    default:
      // Show all integrations for unknown agent types
      return {
        notion: true,
        confluence: true,
        jira: true,
        figma: true,
      };
  }
}

/**
 * Process integration data and set connection states
 * @param integrations - Array of integration data from API
 * @param setters - Object containing setter functions for each integration type
 */
export function processIntegrations(
  integrations: Integration[],
  setters: IntegrationSetters
): void {
  integrations.forEach(integration => {
    if (!integration.is_active) return;

    const connectionState: ConnectionState = {
      isConnected: true,
      id: integration.id,
    };

    switch (integration.type) {
      case 'notion':
        setters.setNotionConnection(connectionState);
        break;
      case 'atlassian':
        setters.setAtlassianMCPConnection(connectionState);
        break;
      case 'github':
        setters.setGitHubConnection(connectionState);
        break;
      case 'figma':
        setters.setFigmaConnection(connectionState);
        break;
      default:
        // Handle unknown integration types gracefully
        console.warn(`Unknown integration type: ${integration.type}`);
        break;
    }
  });
}
