'use client';

import React from 'react';
import Link from 'next/link';
import { PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DataTable, StatusBadge } from '@/components/ui/table';
import { Project, ProjectStatus } from '@/types/api';
import { formatRelativeTime, snakeToTitle } from '@/lib/utils';

export interface RecentProjectsProps {
  projects: Project[];
  loading?: boolean;
  onCreateProject?: () => void;
}

const RecentProjects: React.FC<RecentProjectsProps> = ({
  projects,
  loading = false,
  onCreateProject,
}) => {
  const columns = [
    {
      key: 'name' as keyof Project,
      header: 'Project',
      render: (value: string | number | undefined, project: Project) => (
        <div className="flex items-center space-x-3">
          <div
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{
              backgroundColor: getStatusColor(project.status),
            }}
          />
          <div>
            <Link
              href={`/projects/${project.id}`}
              className="font-medium text-foreground hover:text-primary transition-colors"
            >
              {project.name}
            </Link>
            {project.description && (
              <p className="text-xs text-muted-foreground mt-0.5">
                {project.description}
              </p>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'project_type' as keyof Project,
      header: 'Type',
      render: (value: string | number | undefined) => (
        <span className="px-2 py-1 text-xs font-medium bg-primary/10 text-primary rounded-md">
          {snakeToTitle(String(value || ''))}
        </span>
      ),
    },
    {
      key: 'status' as keyof Project,
      header: 'Status',
      render: (value: string | number | undefined) => (
        <StatusBadge status={String(value || '')} />
      ),
    },
    {
      key: 'updated_at' as keyof Project,
      header: 'Last Updated',
      render: (value: string | number | undefined) => (
        <span className="text-sm text-muted-foreground">
          {formatRelativeTime(String(value || ''))}
        </span>
      ),
    },
  ];

  const getStatusColor = (status: ProjectStatus) => {
    const colors = {
      [ProjectStatus.ACTIVE]: '#10b981',
      [ProjectStatus.INACTIVE]: '#6b7280',
      [ProjectStatus.ARCHIVED]: '#6b7280',
      [ProjectStatus.COMPLETED]: '#10b981',
    };
    return colors[status] || colors[ProjectStatus.INACTIVE];
  };

  if (loading) {
    return (
      <Card variant="glass" className="animate-fade-in">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="h-6 w-32 bg-muted/20 rounded animate-pulse" />
            <div className="flex space-x-3">
              <div className="h-8 w-16 bg-muted/20 rounded animate-pulse" />
              <div className="h-8 w-24 bg-muted/20 rounded animate-pulse" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-muted/10 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="glass" className="animate-fade-in">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl">Recent Projects</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Your latest project activity and updates
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button variant="ghost" size="sm">
              <FunnelIcon className="w-4 h-4 mr-2" />
              Filter
            </Button>
            <Button 
              variant="default" 
              size="sm"
              onClick={onCreateProject}
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {projects.length === 0 ? (
          <div className="text-center py-8">
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
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 5a2 2 0 012-2h4a2 2 0 012 2v0a2 2 0 01-2 2h-4a2 2 0 01-2-2v0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">
              No projects yet
            </h3>
            <p className="text-muted-foreground mb-4">
              Create your first project to start managing your development workflow.
            </p>
            <Button 
              variant="default"
              onClick={onCreateProject}
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              Create Project
            </Button>
          </div>
        ) : (
          <>
            <DataTable
              data={projects.slice(0, 5)}
              columns={columns}
              onRowClick={(project) => {
                window.location.href = `/projects/${project.id}`;
              }}
            />
            
            {projects.length > 5 && (
              <div className="mt-4 pt-4 border-t border-glass-border">
                <Link href="/projects">
                  <Button variant="ghost" className="w-full">
                    View All Projects ({projects.length})
                  </Button>
                </Link>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentProjects;
