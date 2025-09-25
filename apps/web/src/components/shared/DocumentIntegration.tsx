'use client';

import { useState, useMemo } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { File2Icon, FileIcon } from '@/components/icons';
import { FeatureCard } from '@/components/shared/FeatureCard';
import { DocumentationModal } from '@/components/shared/DocumentationModal';
import SectionWrapper from '@/components/shared/SectionWrapper';
import { NotionDocuments } from '@/components/shared/NotionDocuments';
import { ConfluenceDocuments } from '@/components/shared/ConfluenceDocuments';
import { JiraDocuments } from '@/components/shared/JiraDocuments';
import { FigmaDocuments } from '@/components/shared/FigmaDocuments';
import { useOAuth } from '@/hooks/useOAuth';
import { getAvailableIntegrations } from '@/lib/utils/integrationUtils';
import type { DocumentType, SupportedAgentType } from '@/types';
import { PrdIcon } from '../icons/PrdIcon';

interface DocumentIntegrationProps {
  type: DocumentType;
  agentType?: SupportedAgentType;
}

export function DocumentIntegration({
  type,
  agentType,
}: DocumentIntegrationProps) {
  const [showDocumentationModal, setShowDocumentationModal] = useState(false);
  const { notionConnection, atlassianMCPConnection, figmaConnection } =
    useOAuth();

  // Get available integrations based on agent type and document type
  const availableIntegrations = useMemo(
    () => getAvailableIntegrations(agentType, type),
    [agentType, type]
  );

  const hasConnections =
    (notionConnection.isConnected && availableIntegrations.notion) ||
    (atlassianMCPConnection.isConnected && availableIntegrations.confluence) ||
    (atlassianMCPConnection.isConnected && availableIntegrations.jira) ||
    (figmaConnection.isConnected && availableIntegrations.figma);

  // Type-specific content
  const content = {
    prd: {
      title: 'Add PRD Documentation',
      heading: 'Add PRD Documentation',
      subheading:
        'Connect your Product Requirement Documents to help AI understand your product specifications, features, and requirements.',
      buttonText: 'Connect PRD Documentation',
      addButtonText: 'Add PRD Documentation',
    },
    supporting_doc: {
      title: 'Add Supporting Documents (Optional)',
      heading: 'Add Supporting Documents',
      subheading:
        'Integrate your documentation to enhance AI understanding of your systems, workflows, and product requirements.',
      buttonText: 'Connect Supporting Documents',
      addButtonText: 'Add Supporting Documents',
    },
  };

  const typeContent = content[type];

  return (
    <SectionWrapper
      icon={
        type === 'prd' ? (
          <PrdIcon className='h-4 w-4' />
        ) : (
          <FileIcon className='h-4 w-4' />
        )
      }
      title={typeContent.title}
    >
      {!hasConnections ? (
        <FeatureCard
          icon={<File2Icon className='h-10 w-10' />}
          heading={typeContent.heading}
          subheading={typeContent.subheading}
          buttonIcon={<Plus />}
          buttonText={typeContent.buttonText}
          onButtonClick={() => setShowDocumentationModal(true)}
        />
      ) : (
        <div className='space-y-4'>
          {/* Add Knowledge Source Button */}
          <div className='flex justify-end'>
            <Button
              variant='outline'
              size='sm'
              onClick={() => setShowDocumentationModal(true)}
              className='flex items-center gap-2'
            >
              <Plus className='h-4 w-4' />
              {typeContent.addButtonText}
            </Button>
          </div>

          {/* Connected Services */}
          <div className='space-y-3'>
            {notionConnection.isConnected && availableIntegrations.notion && (
              <NotionDocuments type={type} />
            )}
            {atlassianMCPConnection.isConnected &&
              availableIntegrations.confluence && (
                <ConfluenceDocuments type={type} />
              )}
            {atlassianMCPConnection.isConnected &&
              availableIntegrations.jira && <JiraDocuments type={type} />}
            {figmaConnection.isConnected && availableIntegrations.figma && (
              <FigmaDocuments type={type} />
            )}
          </div>
        </div>
      )}

      {/* Documentation Modal */}
      <DocumentationModal
        open={showDocumentationModal}
        onOpenChange={setShowDocumentationModal}
        type={type}
        agentType={agentType}
      />
    </SectionWrapper>
  );
}
