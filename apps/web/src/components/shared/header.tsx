'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  BellIcon, 
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';
import { SearchInput } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { useCurrentUser, useLogout } from '@/hooks/use-api';
import { getInitials, stringToColor } from '@/lib/utils';

export interface HeaderProps {
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ className }) => {
  const router = useRouter();
  const { data: user } = useCurrentUser();
  const logoutMutation = useLogout();

  const handleSearch = (value: string) => {
    // TODO: Implement global search functionality
    console.log('Search:', value);
  };

  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => {
        router.push('/auth/login');
      },
    });
  };

  return (
    <header className={cn(
      'sticky top-0 z-50 glass border-b border-glass-border backdrop-blur-md',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center animate-pulse-subtle">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 2L3 14h10l-1 8 10-12H12l1-8z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  SDLC Agent
                </h1>
                <p className="text-xs text-muted-foreground -mt-1">
                  Intelligent Development Lifecycle
                </p>
              </div>
            </Link>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-lg mx-8">
            <SearchInput
              placeholder="Search projects, agents, workflows..."
              onSearch={handleSearch}
              className="w-full"
              variant="glass"
            />
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <Button
              variant="ghost"
              size="icon"
              className="relative glass-hover"
            >
              <BellIcon className="h-5 w-5" />
              {/* Notification badge */}
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-error rounded-full flex items-center justify-center">
                <span className="text-[10px] text-white font-medium">3</span>
              </span>
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="icon"
              className="glass-hover"
              onClick={() => router.push('/settings')}
            >
              <Cog6ToothIcon className="h-5 w-5" />
            </Button>

            {/* User Menu */}
            <div className="flex items-center space-x-3">
              {user ? (
                <div className="flex items-center space-x-3">
                  {/* User Avatar */}
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{ backgroundColor: stringToColor(user.name) }}
                  >
                    {getInitials(user.name)}
                  </div>
                  
                  {/* User Info */}
                  <div className="hidden sm:block">
                    <p className="text-sm font-medium text-foreground">
                      {user.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {user.email}
                    </p>
                  </div>

                  {/* Logout Button */}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleLogout}
                    className="glass-hover text-muted-foreground hover:text-error"
                    disabled={logoutMutation.isPending}
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push('/auth/login')}
                  >
                    Sign In
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => router.push('/auth/register')}
                  >
                    Sign Up
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
