'use client';

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import Header from './header';
import Sidebar from './sidebar';
import { cn } from '@/lib/utils';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: (failureCount, error: unknown) => {
        if (error && typeof error === 'object' && 'response' in error) {
          const errorResponse = error.response as { status?: number };
          if (errorResponse?.status === 401) {
            return false; // Don't retry on auth errors
          }
        }
        return failureCount < 3;
      },
    },
  },
});

export interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, className }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background text-foreground">
        {/* Animated background */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-background via-muted/20 to-background" />
          
          {/* Floating orbs */}
          <div className="absolute top-20 left-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl animate-pulse-subtle" />
          <div className="absolute top-40 right-20 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '2s' }} />
          <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-accent/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '4s' }} />
        </div>

        {/* Header */}
        <Header />

        <div className="flex">
          {/* Sidebar */}
          <Sidebar 
            collapsed={sidebarCollapsed}
            onCollapse={setSidebarCollapsed}
          />

          {/* Main Content */}
          <main className={cn(
            'flex-1 transition-all duration-300',
            'min-h-[calc(100vh-4rem)]',
            className
          )}>
            <div className="p-6">
              {children}
            </div>
          </main>
        </div>

        {/* Toast notifications */}
        <Toaster 
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'white',
            },
          }}
        />
      </div>
    </QueryClientProvider>
  );
};

export default Layout;
