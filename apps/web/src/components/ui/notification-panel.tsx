'use client';

import React from 'react';
import { X, Check, Warning, Info } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface Notification {
  id: string;
  type: 'success' | 'warning' | 'info' | 'default';
  title: string;
  message: string;
  timestamp: string;
  avatar?: string;
  isRead?: boolean;
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: Notification[];
  onMarkAsRead?: (id: string) => void;
  onClearAll?: () => void;
}

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return <Check size={16} className="text-chart-1" />;
    case 'warning':
      return <Warning size={16} className="text-chart-3" />;
    case 'info':
      return <Info size={16} className="text-chart-5" />;
    default:
      return <div className="w-2 h-2 rounded-full bg-chart-1" />;
  }
};

const getNotificationColor = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return 'border-chart-1/20 bg-chart-1/5';
    case 'warning':
      return 'border-chart-3/20 bg-chart-3/5';
    case 'info':
      return 'border-chart-5/20 bg-chart-5/5';
    default:
      return 'border-border bg-card';
  }
};

export function NotificationPanel({
  isOpen,
  onClose,
  notifications,
  onMarkAsRead,
  onClearAll,
}: NotificationPanelProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed top-0 right-0 h-full w-96 bg-background border-l border-border z-50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Notifications</h2>
            <p className="text-sm text-muted-foreground">
              {notifications.filter(n => !n.isRead).length} unread
            </p>
          </div>
          <div className="flex items-center gap-2">
            {onClearAll && (
              <Button variant="ghost" size="sm" onClick={onClearAll}>
                Clear All
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
              <X size={16} />
            </Button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="overflow-y-auto h-full pb-20">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
                <Info size={24} className="text-muted-foreground" />
              </div>
              <p className="text-muted-foreground">No notifications yet</p>
            </div>
          ) : (
            <div className="p-4 space-y-3">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    'p-4 rounded-xl border transition-all duration-200 cursor-pointer hover:shadow-sm',
                    getNotificationColor(notification.type),
                    !notification.isRead && 'ring-1 ring-primary/20'
                  )}
                  onClick={() => onMarkAsRead?.(notification.id)}
                >
                  <div className="flex items-start gap-3">
                    {/* Avatar or Icon */}
                    <div className="flex-shrink-0">
                      {notification.avatar ? (
                        <img
                          src={notification.avatar}
                          alt=""
                          className="w-8 h-8 rounded-full"
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-muted/50 flex items-center justify-center">
                          {getNotificationIcon(notification.type)}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className={cn(
                          'text-sm font-medium text-foreground truncate',
                          !notification.isRead && 'font-semibold'
                        )}>
                          {notification.title}
                        </h3>
                        <span className="text-xs text-muted-foreground flex-shrink-0">
                          {notification.timestamp}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                    </div>

                    {/* Unread indicator */}
                    {!notification.isRead && (
                      <div className="w-2 h-2 rounded-full bg-chart-1 flex-shrink-0 mt-2" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
