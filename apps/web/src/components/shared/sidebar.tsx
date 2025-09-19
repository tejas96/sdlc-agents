'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  CpuChipIcon,
  DocumentTextIcon,
  Cog8ToothIcon,
  FolderIcon,
  ChartBarIcon,
  UsersIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  CpuChipIcon as CpuChipIconSolid,
  DocumentTextIcon as DocumentTextIconSolid,
  Cog8ToothIcon as Cog8ToothIconSolid,
  FolderIcon as FolderIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  UsersIcon as UsersIconSolid,
  Cog6ToothIcon as Cog6ToothIconSolid,
} from '@heroicons/react/24/solid';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  iconSolid: React.ComponentType<{ className?: string }>;
  description?: string;
  badge?: string | number;
}

const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/',
    icon: HomeIcon,
    iconSolid: HomeIconSolid,
    description: 'Overview and metrics',
  },
  {
    name: 'AI Agents',
    href: '/agents',
    icon: CpuChipIcon,
    iconSolid: CpuChipIconSolid,
    description: 'Manage AI agents',
    badge: 8,
  },
  {
    name: 'Workflows',
    href: '/workflows',
    icon: Cog8ToothIcon,
    iconSolid: Cog8ToothIconSolid,
    description: 'Automation workflows',
  },
  {
    name: 'Integrations',
    href: '/integrations',
    icon: DocumentTextIcon,
    iconSolid: DocumentTextIconSolid,
    description: 'External services',
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderIcon,
    iconSolid: FolderIconSolid,
    description: 'Active projects',
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
    iconSolid: ChartBarIconSolid,
    description: 'Performance insights',
  },
  {
    name: 'Team',
    href: '/team',
    icon: UsersIcon,
    iconSolid: UsersIconSolid,
    description: 'Team management',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Cog6ToothIcon,
    iconSolid: Cog6ToothIconSolid,
    description: 'System settings',
  },
];

export interface SidebarProps {
  className?: string;
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  className, 
  collapsed = false, 
  onCollapse 
}) => {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname.startsWith(href);
  };

  return (
    <aside className={cn(
      'glass border-r border-glass-border backdrop-blur-md transition-all duration-300 ease-in-out',
      collapsed ? 'w-16' : 'w-72',
      'sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto',
      className
    )}>
      <div className="p-4">
        {/* Collapse Toggle */}
        <div className="flex justify-end mb-6">
          <button
            onClick={() => onCollapse?.(!collapsed)}
            className="p-2 rounded-lg glass-hover transition-all duration-200"
          >
            <svg
              className={cn(
                'w-4 h-4 transition-transform duration-200',
                collapsed ? 'rotate-180' : ''
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
              />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navigationItems.map((item) => {
            const active = isActive(item.href);
            const Icon = active ? item.iconSolid : item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 relative group',
                  'hover:bg-primary/10 hover:text-primary hover:translate-x-1',
                  active && 'bg-gradient-to-r from-primary/20 to-secondary/10 text-primary border border-primary/20',
                  !active && 'text-muted-foreground hover:text-foreground',
                  collapsed && 'justify-center'
                )}
              >
                {/* Active indicator */}
                {active && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary to-secondary rounded-r-full" />
                )}

                {/* Icon */}
                <Icon className={cn(
                  'w-5 h-5 flex-shrink-0',
                  !collapsed && 'mr-3'
                )} />

                {/* Content */}
                {!collapsed && (
                  <>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span>{item.name}</span>
                        {item.badge && (
                          <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-primary/20 text-primary rounded-full">
                            {item.badge}
                          </span>
                        )}
                      </div>
                      {item.description && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {item.description}
                        </p>
                      )}
                    </div>
                  </>
                )}

                {/* Tooltip for collapsed state */}
                {collapsed && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-background border border-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 whitespace-nowrap">
                    <div className="text-sm font-medium">{item.name}</div>
                    {item.description && (
                      <div className="text-xs text-muted-foreground">
                        {item.description}
                      </div>
                    )}
                    {item.badge && (
                      <div className="mt-1">
                        <span className="px-2 py-0.5 text-xs font-medium bg-primary/20 text-primary rounded-full">
                          {item.badge}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        {!collapsed && (
          <div className="mt-8 pt-6 border-t border-glass-border">
            <div className="px-3 py-2">
              <p className="text-xs text-muted-foreground">
                SDLC Agent v1.0.0
              </p>
              <p className="text-xs text-muted-foreground">
                © 2025 SDLC Team
              </p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
