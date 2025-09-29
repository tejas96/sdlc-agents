'use client';

import { useState } from 'react';
import { Bell, MagnifyingGlass } from '@phosphor-icons/react';
import { useHeader } from '@/hooks/useHeader';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Button } from '@/components/ui/button';
import { NotificationPanel, type Notification } from '@/components/ui/notification-panel';

// Sample notifications inspired by the reference image
const SAMPLE_NOTIFICATIONS: Notification[] = [
  {
    id: '1',
    type: 'success',
    title: 'Clifford Hale',
    message: 'Team can access your tasks when you finish analysis',
    timestamp: '2 hours ago',
    avatar: '/api/placeholder/32/32',
    isRead: false,
  },
  {
    id: '2',
    type: 'info',
    title: 'Lottie Marsh',
    message: 'Hey for logos have we anything we can change just a bit',
    timestamp: '5 hours ago',
    avatar: '/api/placeholder/32/32',
    isRead: false,
  },
  {
    id: '3',
    type: 'success',
    title: 'BTC News',
    message: 'Bitcoin Cash gets important 5 point kahua bank about',
    timestamp: '6 hours ago',
    isRead: true,
  },
  {
    id: '4',
    type: 'warning',
    title: 'Danny Jacobs',
    message: 'Better bitcoin Lucid master market',
    timestamp: '8 hours ago',
    isRead: true,
  },
];

const Header = () => {
  const { title } = useHeader();
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(SAMPLE_NOTIFICATIONS);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const handleMarkAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, isRead: true } : n)
    );
  };

  const handleClearAll = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  };

  return (
    <>
      <header className='bg-background border-border flex h-16 items-center justify-between border-b px-6 backdrop-blur-sm'>
        <div className='flex items-center gap-4'>
          <h1 className='text-foreground text-xl font-semibold'>{title}</h1>
        </div>

        {/* Right side actions */}
        <div className='flex items-center gap-3'>
          {/* Search Button */}
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0">
            <MagnifyingGlass size={18} className="text-muted-foreground" />
          </Button>

          {/* Notification Bell */}
          <Button
            variant="ghost"
            size="sm"
            className="h-9 w-9 p-0 relative"
            onClick={() => setIsNotificationPanelOpen(true)}
          >
            <Bell size={18} className="text-muted-foreground" />
            {/* Notification dot */}
            {unreadCount > 0 && (
              <div className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-chart-2 flex items-center justify-center">
                <span className="text-xs font-medium text-white">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              </div>
            )}
          </Button>

          {/* Theme Toggle */}
          <ThemeToggle />
        </div>
      </header>

      {/* Notification Panel */}
      <NotificationPanel
        isOpen={isNotificationPanelOpen}
        onClose={() => setIsNotificationPanelOpen(false)}
        notifications={notifications}
        onMarkAsRead={handleMarkAsRead}
        onClearAll={handleClearAll}
      />
    </>
  );
};

export default Header;
