import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { JiraIcon } from '@/components/icons';
import { FileText, Settings, X } from 'lucide-react';
import { JiraTicketsModal } from './JiraTicketsModal';
import { integrationApi } from '@/lib/api/api';
import type {
  AtlassianIssue,
  DocumentType,
  EnhancedAtlassianIssue,
} from '@/types';
import { useOAuth } from '@/hooks/useOAuth';
import { useUser } from '@/hooks/useUser';
import { toast } from 'sonner';
import { useProject } from '@/hooks/useProject';
import { cn } from '@/lib/utils';
import ConfirmModal from './ConfirmModal';

interface JiraDocumentsProps {
  type: DocumentType;
}

export function JiraDocuments({ type }: JiraDocumentsProps) {
  const { resetAtlassianMCPConnection, atlassianMCPConnection } = useOAuth();
  const { accessToken } = useUser();
  const {
    setPrdjira,
    prdjira,
    setDocsjira,
    docsjira,
    resetCachedJiraProjects,
    resetCachedJiraTickets,
  } = useProject();
  const [showModal, setShowModal] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [showDisconnectModal, setShowDisconnectModal] = useState(false);

  const content = {
    prd: {
      title: 'Jira PRD Tickets',
      emptyText: 'No PRD tickets selected.',
      disconnectMessage:
        'Are you sure you want to disconnect Jira? This will remove all PRD tickets and their associated data. This action cannot be undone.',
    },
    supporting_doc: {
      title: 'Jira Tickets',
      emptyText: 'No tickets selected.',
      disconnectMessage:
        'Are you sure you want to disconnect Jira? This will remove all tickets and their associated data. This action cannot be undone.',
    },
  };

  const currentData = type === 'prd' ? prdjira : docsjira;
  const { title, emptyText } = content[type];

  // Get issue type color
  const getIssueTypeColor = (issueType: string) => {
    switch (issueType?.toLowerCase()) {
      case 'story':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'bug':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'task':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'epic':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'highest':
      case 'blocker':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-pink-100 text-pink-800 border-pink-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'lowest':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const handleDisconnect = async () => {
    if (!accessToken) return;

    setIsDisconnecting(true);
    try {
      const response = await integrationApi.delete(
        atlassianMCPConnection.id,
        accessToken
      );

      if (response.success) {
        resetAtlassianMCPConnection();
        setPrdjira({ tickets: [], selectedTickets: [] });
        resetCachedJiraProjects();
        resetCachedJiraTickets();
        toast.success('Jira disconnected successfully');
        setShowDisconnectModal(false);
      } else {
        toast.error(
          `Failed to disconnect: ${response.error || 'Unknown error'}`
        );
      }
    } catch {
      toast.error('Failed to disconnect Jira');
    } finally {
      setIsDisconnecting(false);
    }
  };

  const handleConfirm = (
    selectedTickets: EnhancedAtlassianIssue[],
    ticketIds: string[]
  ) => {
    const setter = type === 'prd' ? setPrdjira : setDocsjira;
    setter({ tickets: selectedTickets, selectedTickets: ticketIds });
    setShowModal(false);
  };

  const handleRemoveTicket = (ticketId: string) => {
    const setter = type === 'prd' ? setPrdjira : setDocsjira;
    const filteredTickets = currentData.tickets.filter(
      ticket => ticket.id !== ticketId
    );
    const filteredSelectedTickets = currentData.selectedTickets.filter(
      id => id !== ticketId
    );

    setter({
      tickets: filteredTickets,
      selectedTickets: filteredSelectedTickets,
    });
  };

  const handleDisconnectClick = () => {
    setShowDisconnectModal(true);
  };

  return (
    <>
      <div className='bg-card rounded-lg border p-4'>
        <div className='mb-4 flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <JiraIcon className='h-5 w-5' />
            <h3 className='font-medium'>{title}</h3>
          </div>

          <div className='flex items-center gap-2'>
            <Button
              variant='outline'
              size='sm'
              onClick={() => setShowModal(true)}
              className='gap-2'
            >
              <Settings className='h-4 w-4' />
              Manage
            </Button>
            <Button
              variant='outline'
              size='sm'
              onClick={handleDisconnectClick}
              className='border-red-700 bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-900'
            >
              Disconnect
            </Button>
          </div>
        </div>

        <div>
          {currentData.tickets.length === 0 ? (
            <div className='py-4 text-center'>
              <FileText className='text-muted-foreground mx-auto h-8 w-8' />
              <p className='text-muted-foreground mt-2 text-sm'>{emptyText}</p>
              <p className='text-muted-foreground mt-1 text-xs'>
                Click &ldquo;Manage&rdquo; to select tickets.
              </p>
            </div>
          ) : (
            <div className='max-h-[400px] overflow-y-auto'>
              {currentData.tickets.map((ticket: AtlassianIssue) => (
                <div
                  key={ticket.id}
                  className='bg-background relative border-b p-4'
                >
                  {/* Remove button */}
                  <button
                    onClick={() => handleRemoveTicket(ticket.id)}
                    className='text-muted-foreground/60 hover:bg-muted hover:text-foreground absolute top-4 right-4 rounded-full p-1 transition-all duration-200'
                    title='Remove this ticket'
                  >
                    <X className='h-4 w-4' />
                  </button>

                  <div className='space-y-2 pr-8'>
                    {/* Issue type and Priority badges */}
                    <div className='flex items-center gap-2'>
                      <Badge
                        variant='outline'
                        className={cn(
                          'text-xs font-medium',
                          getIssueTypeColor(ticket.fields?.issuetype?.name)
                        )}
                      >
                        {ticket.fields?.issuetype?.name}
                      </Badge>
                      <Badge
                        variant='outline'
                        className={cn(
                          'text-xs font-medium',
                          getPriorityColor(ticket.fields?.priority?.name)
                        )}
                      >
                        {ticket.fields?.priority?.name}
                      </Badge>
                    </div>

                    {/* Ticket key */}
                    <div className='text-sm font-semibold text-gray-700'>
                      {ticket.key}
                    </div>

                    {/* Ticket summary/title */}
                    <h4 className='text-xs font-medium text-gray-900'>
                      {ticket.fields?.summary}
                    </h4>

                    {/* Description or acceptance criteria preview */}
                    {ticket.fields?.description && (
                      <div className='mt-2'>
                        <p className='text-xs font-medium text-gray-500'>
                          Acceptance Criteria:
                        </p>
                        <div className='mt-1 space-y-1 text-xs text-gray-600'>
                          {/* Parse and show bullet points from description */}
                          {typeof ticket.fields?.description === 'string' &&
                            ticket.fields.description
                              .split('\n')
                              .filter(line => line.trim())
                              .slice(0, 3)
                              .map((line, idx) => (
                                <div key={idx} className='flex gap-2'>
                                  <span className='text-gray-400'>•</span>
                                  <span className='flex-1'>
                                    {line.trim().replace(/^[-*•]\s*/, '')}
                                  </span>
                                </div>
                              ))}
                          {typeof ticket.fields?.description === 'string' &&
                            ticket.fields?.description
                              .split('\n')
                              .filter(line => line.trim()).length > 3 && (
                              <span className='text-gray-400'>
                                +{' '}
                                {ticket.fields?.description
                                  .split('\n')
                                  .filter(line => line.trim()).length - 3}{' '}
                                more
                              </span>
                            )}
                        </div>
                      </div>
                    )}

                    {/* Additional metadata */}
                    <div className='flex items-center gap-3 text-xs text-gray-500'>
                      {(ticket as any).projectName && (
                        <>
                          <span className='flex items-center gap-1'>
                            <span className='font-medium'>Project:</span>
                            {(ticket as any).projectName}
                          </span>
                          <span className='text-gray-400'>•</span>
                        </>
                      )}
                      <span className='flex items-center gap-1'>
                        <span className='font-medium'>Status:</span>
                        {ticket.fields?.status?.name}
                      </span>
                      {ticket.fields?.assignee && (
                        <>
                          <span className='text-gray-400'>•</span>
                          <span className='flex items-center gap-1'>
                            <span className='font-medium'>Assignee:</span>
                            {ticket.fields?.assignee?.displayName}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <JiraTicketsModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirm}
        type={type}
      />

      {/* Disconnect Confirmation Modal */}
      <ConfirmModal
        open={showDisconnectModal}
        message={content[type]?.disconnectMessage}
        onClose={() => setShowDisconnectModal(false)}
        onConfirm={handleDisconnect}
        isLoading={isDisconnecting}
      />
    </>
  );
}
