'use client';

import { useState, useMemo } from 'react';
import { BookOpenText, X } from 'lucide-react';
import { NotionIcon, ConfluenceIcon, FigmaIcon } from '@/components/icons';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { useOAuth } from '@/hooks/useOAuth';
import { FigmaModal } from './FigmaModal';
import { getAvailableIntegrations } from '@/lib/utils/integrationUtils';

type DocumentType = 'prd' | 'supporting_doc';

interface DocumentationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  type: DocumentType;
  agentType?: string;
}

export function DocumentationModal({
  open,
  onOpenChange,
  type,
  agentType = 'default',
}: DocumentationModalProps) {
  const { notionConnection, atlassianMCPConnection, figmaConnection } =
    useOAuth();
  const [showFigmaModal, setShowFigmaModal] = useState(false);

  const handleConnect = (provider: string) => {
    if (provider === 'figma') {
      setShowFigmaModal(true);
    } else {
      window.location.href = `/api/auth/${provider}?from=${window.location.href}`;
    }
  };

  // Type-specific content
  const content = {
    prd: {
      title: 'Connect Your PRD Source',
      description:
        'Link your PRD tool to help the AI understand your product requirements.',
    },
    supporting_doc: {
      title: 'Add Supporting Documentation',
      description:
        'Integrate your documentation to enhance AI understanding of your systems, workflows, and product requirements.',
    },
  };

  const typeContent = content[type];

  const availableIntegrations = useMemo(
    () => getAvailableIntegrations(agentType, type),
    [agentType, type]
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='sm:max-w-[600px]'>
        <DialogHeader>
          <DialogTitle className='flex items-center gap-3 text-2xl'>
            <span className='text-2xl'>
              <BookOpenText className='h-7 w-7' />
            </span>
            {typeContent.title}
          </DialogTitle>
          <DialogDescription className='pt-2 text-base'>
            {typeContent.description}
          </DialogDescription>
        </DialogHeader>

        <div className='mt-6 space-y-4'>
          {/* Notion Option */}
          {availableIntegrations.notion && (
            <button
              disabled={notionConnection.isConnected}
              onClick={() => handleConnect('notion')}
              className='flex w-full items-center justify-between rounded-lg border border-gray-200 px-4 py-2 transition-all hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50'
            >
              <div className='flex items-center gap-4'>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100'>
                  <NotionIcon className='h-6 w-6' />
                </div>
                <div className='text-left'>
                  <h3 className='text-lg font-semibold'>Connect to Notion</h3>
                  <p className='text-muted-foreground text-sm'>
                    {notionConnection.isConnected
                      ? 'Connected'
                      : 'Not connected'}
                  </p>
                </div>
              </div>
            </button>
          )}

          {/* Confluence Option */}
          {(availableIntegrations.confluence || availableIntegrations.jira) && (
            <button
              disabled={atlassianMCPConnection.isConnected}
              onClick={() => handleConnect('atlassian-mcp')}
              className='flex w-full items-center justify-between rounded-lg border border-gray-200 px-4 py-2 transition-all hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50'
            >
              <div className='flex items-center gap-4'>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100'>
                  <ConfluenceIcon className='h-6 w-6' />
                </div>
                <div className='text-left'>
                  <h3 className='text-lg font-semibold'>
                    Connect to Atlassian
                  </h3>
                  <p className='text-muted-foreground text-sm'>
                    {atlassianMCPConnection.isConnected
                      ? 'Connected'
                      : 'Not connected'}
                  </p>
                </div>
              </div>
            </button>
          )}

          {/* Figma Option */}
          {availableIntegrations.figma && (
            <button
              disabled={figmaConnection.isConnected}
              onClick={() => handleConnect('figma')}
              className='flex w-full items-center justify-between rounded-lg border border-gray-200 px-4 py-2 transition-all hover:border-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50'
            >
              <div className='flex items-center gap-4'>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100'>
                  <FigmaIcon className='h-6 w-6' />
                </div>
                <div className='text-left'>
                  <h3 className='text-lg font-semibold'>Connect to Figma</h3>
                  <p className='text-muted-foreground text-sm'>
                    {figmaConnection.isConnected
                      ? 'Connected'
                      : 'Not connected'}
                  </p>
                </div>
              </div>
            </button>
          )}
        </div>

        {/* Custom close button */}
        <button
          onClick={() => onOpenChange(false)}
          className='ring-offset-background focus:ring-ring absolute top-4 right-22 rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-offset-2 focus:outline-none'
        >
          <X className='h-4 w-4' />
          <span className='sr-only'>Close</span>
        </button>
      </DialogContent>

      {/* Figma Modal */}
      <FigmaModal open={showFigmaModal} onOpenChange={setShowFigmaModal} />
    </Dialog>
  );
}
