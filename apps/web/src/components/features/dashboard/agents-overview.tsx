'use client';

import React from 'react';
import Link from 'next/link';
import { PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { AgentCard } from '@/components/ui/card';
import { Agent } from '@/types/api';
import { useExecuteAgent } from '@/hooks/use-api';

export interface AgentsOverviewProps {
  agents: Agent[];
  loading?: boolean;
  onCreateAgent?: () => void;
}

const AgentsOverview: React.FC<AgentsOverviewProps> = ({
  agents,
  loading = false,
  onCreateAgent,
}) => {
  const executeAgentMutation = useExecuteAgent();

  const handleExecuteAgent = (agentId: number) => {
    executeAgentMutation.mutate(agentId);
  };

  const handleEditAgent = (agentId: number) => {
    // TODO: Implement edit functionality
    console.log('Edit agent:', agentId);
  };

  const handleDeleteAgent = (agentId: number) => {
    // TODO: Implement delete functionality
    console.log('Delete agent:', agentId);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="flex items-center justify-between">
          <div className="h-8 w-48 bg-muted/20 rounded animate-pulse" />
          <div className="flex space-x-3">
            <div className="h-10 w-20 bg-muted/20 rounded animate-pulse" />
            <div className="h-10 w-32 bg-muted/20 rounded animate-pulse" />
          </div>
        </div>

        {/* Cards skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-64 glass rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            AI Agent Ecosystem
          </h2>
          <p className="text-muted-foreground mt-1">
            Manage and monitor your intelligent development agents
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="ghost" size="sm">
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button 
            variant="gradient" 
            size="sm"
            onClick={onCreateAgent}
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Deploy Agent
          </Button>
        </div>
      </div>

      {/* Agents Grid */}
      {agents.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full glass flex items-center justify-center">
            <svg
              className="w-12 h-12 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-foreground mb-2">
            No agents deployed yet
          </h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Get started by deploying your first AI agent to automate your development workflow.
          </p>
          <Button 
            variant="gradient"
            onClick={onCreateAgent}
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            Deploy Your First Agent
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.slice(0, 6).map((agent, index) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onExecute={handleExecuteAgent}
              onEdit={handleEditAgent}
              onDelete={handleDeleteAgent}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            />
          ))}
        </div>
      )}

      {/* View All Link */}
      {agents.length > 6 && (
        <div className="text-center pt-6">
          <Link href="/agents">
            <Button variant="ghost">
              View All Agents ({agents.length})
              <svg
                className="w-4 h-4 ml-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
};

export default AgentsOverview;
