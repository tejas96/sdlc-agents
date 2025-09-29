'use client';

import Sidebar from '@/components/shared/sidebar';
import Header from '@/components/shared/header';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className='bg-background flex h-screen'>
      <Sidebar />
      <div className='flex flex-1 flex-col overflow-hidden'>
        <Header />
        <main className='flex-1 overflow-auto bg-background p-6'>{children}</main>
      </div>
    </div>
  );
};

export default MainLayout;
