import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { persist } from 'zustand/middleware';

interface HeaderState {
  title: string;
  setTitle: (title: string) => void;
  resetTitle: () => void;
  isCollapsed: boolean;
  setIsCollapsed: (isCollapsed: boolean) => void;
  resetIsCollapsed: () => void;
  resetAll: () => void;
}

export const useHeaderStore = create<HeaderState>()(
  devtools(
    persist(
      set => ({
        title: 'Optima AI',
        setTitle: (title: string) => set(() => ({ title })),
        resetTitle: () => set(() => ({ title: 'Optima AI' })),
        isCollapsed: false,
        setIsCollapsed: (isCollapsed: boolean) => set(() => ({ isCollapsed })),
        resetIsCollapsed: () => set(() => ({ isCollapsed: false })),
        resetAll: () => set(() => ({ title: 'Optima AI', isCollapsed: false })),
      }),
      {
        name: 'header-store',
      }
    ),
    {
      name: 'header-store',
    }
  )
);
