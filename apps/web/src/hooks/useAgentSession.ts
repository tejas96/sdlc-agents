import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { sessionApi } from '@/lib/api/api';
import { useUser } from './useUser';
import { useProject } from './useProject';
import type {
  CreateSessionOptions,
  SupportedAgentType,
  SelectedNotionPage,
} from '@/types';
import { useOAuth } from './useOAuth';
export function useAgentSession() {
  const router = useRouter();
  const { accessToken } = useUser();
  const { atlassianMCPConnection } = useOAuth();
  const {
    projectName,
    analysisType,
    aiEngine,
    userPrompt,
    agentType,
    gitHubRepos,
    prdnotion,
    prdconfluence,
    prdjira,
    prdfigma,
    docsnotion,
    docsconfluence,
    docsfigma,
    docsjira,
    output_config_type,
    output_config_content,
    output,
  } = useProject();

  const [isCreatingSession, setIsCreatingSession] = useState(false);

  // Build MCP agents list based on selected integrations
  const mcpAgents = useMemo(() => {
    const mcpAgentsSet = new Set<string>();

    // Check for Notion usage
    if (
      prdnotion.selectedPages.length > 0 ||
      docsnotion.selectedPages.length > 0
    ) {
      mcpAgentsSet.add('notion');
    }

    // Check for Confluence usage
    if (
      prdconfluence.selectedPages.length > 0 ||
      docsconfluence.selectedPages.length > 0
    ) {
      mcpAgentsSet.add('atlassian');
    }

    // Check for Jira usage
    if (
      prdjira.selectedTickets.length > 0 ||
      docsjira.selectedTickets.length > 0
    ) {
      mcpAgentsSet.add('atlassian');
    }

    // Check for Figma usage
    if (
      prdfigma.selectedFiles.length > 0 ||
      docsfigma.selectedFiles.length > 0
    ) {
      mcpAgentsSet.add('figma');
    }

    // Check for GitHub usage
    if (gitHubRepos.selectedRepositories.length > 0 || gitHubRepos.selectedPR) {
      mcpAgentsSet.add('github');
    }

    // Check for Atlassian MCP usage
    if (
      agentType === 'requirements_to_tickets' &&
      atlassianMCPConnection.isConnected
    ) {
      mcpAgentsSet.add('atlassian');
    }

    return Array.from(mcpAgentsSet);
  }, [
    prdnotion.selectedPages,
    docsnotion.selectedPages,
    prdconfluence.selectedPages,
    docsconfluence.selectedPages,
    prdjira.selectedTickets,
    docsjira.selectedTickets,
    prdfigma.selectedFiles,
    docsfigma.selectedFiles,
    gitHubRepos.selectedRepositories,
    gitHubRepos.selectedPR,
  ]);

  const buildSessionPayload = useMemo(() => {
    const buildPayload = (): any => {
      // Base structure - always included
      const payload: any = {
        project_name: projectName,
        mcps: mcpAgents,
        custom_properties: {
          custom_instructions: userPrompt,
          ai_engine: aiEngine,
        },
      };

      // Agent-specific payload building
      switch (agentType as SupportedAgentType) {
        case 'code_analysis':
          // Add analysis type for code analysis
          payload.custom_properties.analysis_type = analysisType;

          // Add GitHub repositories if selected
          if (gitHubRepos.selectedRepositories.length > 0) {
            payload.custom_properties.github_repos =
              gitHubRepos.selectedRepositories;
          }

          // Add documentation sources for code analysis
          const codeAnalysisDocs = [];
          if (docsnotion.selectedPages.length > 0) {
            codeAnalysisDocs.push({
              provider: 'Notion',
              urls: docsnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.url
              ),
            });
          }
          if (docsconfluence.selectedPages.length > 0) {
            codeAnalysisDocs.push({
              provider: 'Confluence',
              ids: docsconfluence.selectedPages,
            });
          }
          if (codeAnalysisDocs.length > 0) {
            payload.custom_properties.docs = codeAnalysisDocs;
          }
          break;

        case 'code_reviewer':
          // Code Reviewer Agent - use analysis_level and inputs structure
          payload.custom_properties.analysis_level = analysisType || 'basic';

          // Add selected PR data as inputs
          const codeReviewInputs = [];
          if (gitHubRepos.selectedPR) {
            codeReviewInputs.push({
              provider: 'github',
              type: 'pr',
              urls: [gitHubRepos.selectedPR.html_url],
            });
          }

          if (codeReviewInputs.length > 0) {
            payload.custom_properties.inputs = codeReviewInputs;
          }

          // Add documentation sources for code reviewer
          const codeReviewDocs = [];
          if (docsnotion.selectedPages.length > 0) {
            codeReviewDocs.push({
              provider: 'Notion',
              urls: docsnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.url
              ),
            });
          }
          if (docsconfluence.selectedPages.length > 0) {
            codeReviewDocs.push({
              provider: 'Confluence',
              ids: docsconfluence.selectedPages,
            });
          }
          if (codeReviewDocs.length > 0) {
            payload.custom_properties.docs = codeReviewDocs;
          }

          break;

        case 'test_case_generation':
          // For test case generation, use individual input objects
          const testGenInputs = [];

          if (prdnotion.selectedPages.length > 0) {
            testGenInputs.push(
              ...prdnotion.selectedPages.map((page: SelectedNotionPage) => ({
                type: 'document',
                provider: 'Notion',
                id: page.id,
                url: page.url,
              }))
            );
          }

          if (prdconfluence.selectedPages.length > 0) {
            testGenInputs.push(
              ...prdconfluence.selectedPages.map((id: string) => ({
                type: 'document',
                provider: 'Confluence',
                id: id,
              }))
            );
          }

          if (prdjira.selectedTickets.length > 0) {
            testGenInputs.push(
              ...prdjira.selectedTickets.map((key: string) => ({
                type: 'issue',
                provider: 'Jira',
                key: key,
              }))
            );
          }

          if (testGenInputs.length > 0) {
            payload.custom_properties.inputs = testGenInputs;
          }

          // Add documentation sources for test generation
          const testGenDocs = [];
          if (docsnotion.selectedPages.length > 0) {
            testGenDocs.push({
              provider: 'Notion',
              urls: docsnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.url
              ),
            });
          }
          if (docsconfluence.selectedPages.length > 0) {
            testGenDocs.push({
              provider: 'Confluence',
              ids: docsconfluence.selectedPages,
            });
          }
          if (docsfigma.selectedFiles.length > 0) {
            testGenDocs.push({
              provider: 'Figma',
              urls: docsfigma.selectedFiles,
            });
          }
          if (docsjira.selectedTickets.length > 0) {
            testGenDocs.push({
              provider: 'Jira',
              keys: docsjira.selectedTickets,
            });
          }

          if (testGenDocs.length > 0) {
            payload.custom_properties.docs = testGenDocs;
          }

          // Add output configuration if specified
          if (
            output_config_type.length > 0 ||
            output_config_content.length > 0
          ) {
            payload.custom_properties.output_config = {
              type: output_config_type,
              contents: output_config_content,
            };
          }
          break;

        case 'requirements_to_tickets':
          // Use descriptive_level instead of analysis_type
          payload.custom_properties.descriptive_level = analysisType;

          // For requirements_to_tickets: group inputs by provider
          const reqToTicketsInputs = [];

          if (prdnotion.selectedPages.length > 0) {
            reqToTicketsInputs.push({
              type: 'document',
              provider: 'Notion',
              ids: prdnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.id
              ),
              urls: prdnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.url
              ),
            });
          }

          if (prdconfluence.selectedPages.length > 0) {
            reqToTicketsInputs.push({
              type: 'document',
              provider: 'Confluence',
              ids: prdconfluence.selectedPages,
            });
          }

          if (prdjira.selectedTickets.length > 0) {
            reqToTicketsInputs.push({
              type: 'epic',
              provider: 'Jira',
              keys: prdjira.selectedTickets,
            });
          }

          if (reqToTicketsInputs.length > 0) {
            payload.custom_properties.inputs = reqToTicketsInputs;
          }

          // Add documentation sources
          const reqToTicketsDocs = [];
          if (docsnotion.selectedPages.length > 0) {
            reqToTicketsDocs.push({
              provider: 'Notion',
              urls: docsnotion.selectedPages.map(
                (page: SelectedNotionPage) => page.url
              ),
            });
          }
          if (docsconfluence.selectedPages.length > 0) {
            reqToTicketsDocs.push({
              provider: 'Confluence',
              ids: docsconfluence.selectedPages,
            });
          }
          if (docsfigma.selectedFiles.length > 0) {
            reqToTicketsDocs.push({
              provider: 'Figma',
              urls: docsfigma.selectedFiles,
            });
          }
          if (docsjira.selectedTickets.length > 0) {
            reqToTicketsDocs.push({
              provider: 'Jira',
              keys: docsjira.selectedTickets,
            });
          }

          if (reqToTicketsDocs.length > 0) {
            payload.custom_properties.docs = reqToTicketsDocs;
          }

          // Add outputs if specified
          if (output && output.length > 0) {
            payload.custom_properties.outputs = output;
          }
          break;

        default:
          break;
      }

      return payload;
    };

    return buildPayload;
  }, [
    projectName,
    mcpAgents,
    userPrompt,
    analysisType,
    aiEngine,
    agentType,
    gitHubRepos.selectedRepositories,
    gitHubRepos.selectedPR,
    prdnotion.selectedPages,
    prdconfluence.selectedPages,
    prdjira.selectedTickets,
    docsnotion.selectedPages,
    docsconfluence.selectedPages,
    docsfigma.selectedFiles,
    docsjira.selectedTickets,
    output,
    output_config_type,
    output_config_content,
  ]);

  const createSession = async (options: CreateSessionOptions = {}) => {
    // Check if user is authenticated
    if (!accessToken) {
      toast.error('Please login to create a session');
      router.push('/login');
      return null;
    }

    // Check if agent type is set
    if (!agentType) {
      toast.error('Agent type not set. Please go back and select an agent.');
      return null;
    }

    try {
      setIsCreatingSession(true);
      const sessionPayload = buildSessionPayload();

      const response = await sessionApi.createSession(
        accessToken,
        agentType,
        sessionPayload
      );

      if (response.success && response.data) {
        const sessionId = response.data.session_id.toString();

        if (options.onSuccess) {
          options.onSuccess(sessionId);
        }

        return sessionId;
      } else {
        throw new Error('Session creation failed - no data returned');
      }
    } catch (error) {
      console.error('Error creating session:', error);
      toast.error('Failed to create session. Please try again.');
      return null;
    } finally {
      setIsCreatingSession(false);
    }
  };

  return {
    createSession,
    isCreatingSession,
    buildSessionPayload,
    mcpAgents,
  };
}
