'use client';

import React from 'react';
import { 
  CpuChipIcon,
  CheckCircleIcon,
  ClockIcon,
  BoltIcon,
} from '@heroicons/react/24/outline';
import { StatCard } from '@/components/ui/card';
import { formatNumber } from '@/lib/utils';

export interface StatsData {
  activeAgents: number;
  tasksCompleted: number;
  avgResponseTime: string;
  systemUptime: string;
  trends?: {
    activeAgents: number;
    tasksCompleted: number;
    avgResponseTime: number;
    systemUptime: number;
  };
}

export interface StatsGridProps {
  data: StatsData;
  loading?: boolean;
}

const StatsGrid: React.FC<StatsGridProps> = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-32 glass rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  const stats = [
    {
      title: 'Active Agents',
      value: data.activeAgents,
      icon: <CpuChipIcon className="w-6 h-6" />,
      color: 'secondary' as const,
      trend: data.trends ? {
        value: data.trends.activeAgents,
        isPositive: data.trends.activeAgents >= 0,
      } : undefined,
    },
    {
      title: 'Tasks Completed',
      value: formatNumber(data.tasksCompleted),
      icon: <CheckCircleIcon className="w-6 h-6" />,
      color: 'success' as const,
      trend: data.trends ? {
        value: data.trends.tasksCompleted,
        isPositive: data.trends.tasksCompleted >= 0,
      } : undefined,
    },
    {
      title: 'Avg Response Time',
      value: data.avgResponseTime,
      icon: <ClockIcon className="w-6 h-6" />,
      color: data.trends?.avgResponseTime && data.trends.avgResponseTime > 0 ? 'warning' as const : 'primary' as const,
      trend: data.trends ? {
        value: Math.abs(data.trends.avgResponseTime),
        isPositive: data.trends.avgResponseTime <= 0, // Lower response time is better
      } : undefined,
    },
    {
      title: 'System Uptime',
      value: data.systemUptime,
      icon: <BoltIcon className="w-6 h-6" />,
      color: 'success' as const,
      trend: data.trends ? {
        value: data.trends.systemUptime,
        isPositive: data.trends.systemUptime >= 0,
      } : undefined,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <StatCard
          key={stat.title}
          title={stat.title}
          value={stat.value}
          icon={stat.icon}
          color={stat.color}
          trend={stat.trend}
          className="animate-fade-in"
          style={{ animationDelay: `${index * 100}ms` }}
        />
      ))}
    </div>
  );
};

export default StatsGrid;
