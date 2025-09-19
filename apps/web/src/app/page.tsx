'use client';

import React from 'react';
import StatsGrid from '@/components/features/dashboard/stats-grid';
import AgentsOverview from '@/components/features/dashboard/agents-overview';
import RecentProjects from '@/components/features/dashboard/recent-projects';
import { useAgents, useProjects } from '@/hooks/use-api';

export default function DashboardPage() {
  const { data: agentsData, isLoading: agentsLoading } = useAgents({ limit: 6 });
  const { data: projects, isLoading: projectsLoading } = useProjects({ limit: 5 });

  // Mock dashboard stats for now - in real app this would come from API
  const statsData = {
    activeAgents: agentsData?.agents?.filter(a => a.status === 'active').length || 0,
    tasksCompleted: agentsData?.agents?.reduce((sum, a) => sum + a.successful_executions, 0) || 0,
    avgResponseTime: '2.4h',
    systemUptime: '98.7%',
    trends: {
      activeAgents: 24,
      tasksCompleted: 18,
      avgResponseTime: -12,
      systemUptime: 31,
    },
  };

  const handleCreateAgent = () => {
    // TODO: Implement create agent modal
    console.log('Create agent');
  };

  const handleCreateProject = () => {
    // TODO: Implement create project modal
    console.log('Create project');
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">
          Welcome to SDLC Agent
        </h1>
        <p className="text-muted-foreground text-lg">
          Monitor your intelligent development lifecycle with real-time insights and automation.
        </p>
      </div>

      {/* Stats Grid */}
      <StatsGrid 
        data={statsData} 
        loading={agentsLoading}
      />

      {/* Agents Overview */}
      <AgentsOverview
        agents={agentsData?.agents || []}
        loading={agentsLoading}
        onCreateAgent={handleCreateAgent}
      />

      {/* Recent Projects */}
      <RecentProjects
        projects={projects || []}
        loading={projectsLoading}
        onCreateProject={handleCreateProject}
      />
    </div>
  );
}