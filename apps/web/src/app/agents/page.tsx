'use client';

import React, { useState } from 'react';
import { PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DataTable, StatusBadge } from '@/components/ui/table';
import { FormModal } from '@/components/ui/modal';
import { Input, Textarea } from '@/components/ui/input';
import AgentChat from '@/components/features/agents/agent-chat';
import { useAgents, useCreateAgent } from '@/hooks/use-api';
import { Agent, AgentType, AgentCreate } from '@/types/api';
import { formatRelativeTime, snakeToTitle } from '@/lib/utils';

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState<Partial<AgentCreate>>({
    agent_type: AgentType.CODE_REVIEWER,
    model_name: 'claude-3-haiku',
    max_tokens: 4000,
    temperature: 0.1,
    timeout_seconds: 300,
  });

  const { data: agentsData, isLoading } = useAgents();
  const createAgentMutation = useCreateAgent();

  const agents = agentsData?.agents || [];

  const columns = [
    {
      key: 'name' as keyof Agent,
      header: 'Agent',
      sortable: true,
      render: (value: string | number | undefined, agent: Agent) => (
        <div>
          <div className="font-medium text-foreground">{agent.name}</div>
          <div className="text-sm text-muted-foreground">
            {snakeToTitle(agent.agent_type)}
          </div>
        </div>
      ),
    },
    {
      key: 'status' as keyof Agent,
      header: 'Status',
      render: (value: string | number | undefined) => (
        <StatusBadge status={String(value || '')} />
      ),
    },
    {
      key: 'total_executions' as keyof Agent,
      header: 'Executions',
      sortable: true,
      render: (value: string | number | undefined, agent: Agent) => (
        <div className="text-center">
          <div className="font-medium">{agent.total_executions}</div>
          <div className="text-xs text-muted-foreground">
            {agent.successful_executions} successful
          </div>
        </div>
      ),
    },
    {
      key: 'last_execution_at' as keyof Agent,
      header: 'Last Run',
      render: (value: string | number | undefined) => (
        <span className="text-sm text-muted-foreground">
          {value ? formatRelativeTime(String(value)) : 'Never'}
        </span>
      ),
    },
    {
      key: 'id' as keyof Agent,
      header: 'Actions',
      render: (value: string | number | undefined, agent: Agent) => (
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedAgent(agent)}
          >
            Chat
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => console.log('Edit agent:', agent.id)}
          >
            Edit
          </Button>
        </div>
      ),
    },
  ];

  const handleCreateAgent = async () => {
    if (!createForm.name || !createForm.slug) return;

    createAgentMutation.mutate(createForm as AgentCreate, {
      onSuccess: () => {
        setShowCreateModal(false);
        setCreateForm({
          agent_type: AgentType.CODE_REVIEWER,
          model_name: 'claude-3-haiku',
          max_tokens: 4000,
          temperature: 0.1,
          timeout_seconds: 300,
        });
      },
    });
  };

  const handleFileUpload = (files: FileList) => {
    // TODO: Implement file upload to agent session
    console.log('Files uploaded:', files);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Agents</h1>
          <p className="text-muted-foreground mt-1">
            Manage and interact with your intelligent development agents
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="ghost">
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button 
            variant="gradient"
            onClick={() => setShowCreateModal(true)}
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Deploy Agent
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agents List */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle>Your Agents</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              data={agents}
              columns={columns}
              loading={isLoading}
              emptyMessage="No agents deployed yet"
              onRowClick={(agent) => setSelectedAgent(agent)}
            />
          </CardContent>
        </Card>

        {/* Agent Chat Interface */}
        <div>
          {selectedAgent ? (
            <AgentChat
              agent={selectedAgent}
              onFileUpload={handleFileUpload}
            />
          ) : (
            <Card variant="glass" className="h-[600px] flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full glass flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-muted-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Select an Agent
                </h3>
                <p className="text-muted-foreground">
                  Choose an agent from the list to start a conversation
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Create Agent Modal */}
      <FormModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        title="Deploy New Agent"
        description="Create and configure a new AI agent for your development workflow"
        onSubmit={handleCreateAgent}
        loading={createAgentMutation.isPending}
        submitText="Deploy Agent"
      >
        <div className="space-y-4">
          <Input
            label="Agent Name"
            placeholder="Enter agent name"
            value={createForm.name || ''}
            onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
            required
          />
          
          <Input
            label="Slug"
            placeholder="agent-slug"
            value={createForm.slug || ''}
            onChange={(e) => setCreateForm(prev => ({ ...prev, slug: e.target.value }))}
            description="URL-friendly identifier for the agent"
            required
          />
          
          <Textarea
            label="Description"
            placeholder="Describe what this agent does..."
            value={createForm.description || ''}
            onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
          />
          
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Agent Type
            </label>
            <select
              className="w-full h-10 px-3 py-2 rounded-lg border border-border bg-background text-foreground"
              value={createForm.agent_type}
              onChange={(e) => setCreateForm(prev => ({ ...prev, agent_type: e.target.value as AgentType }))}
            >
              {Object.values(AgentType).map((type) => (
                <option key={type} value={type}>
                  {snakeToTitle(type)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </FormModal>
    </div>
  );
}
