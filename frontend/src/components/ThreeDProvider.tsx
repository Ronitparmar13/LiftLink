import { type ReactNode } from 'react';
import { ThreeDContext } from '@/contexts/ThreeDContext';

interface ThreeDProviderProps {
  children: ReactNode;
}

export const ThreeDProvider = ({ children }: ThreeDProviderProps) => {
  const value = { isSupported: false, isEnabled: false, toggleEnabled: () => {} };

  return (
    <ThreeDContext.Provider value={value}>
      {children}
    </ThreeDContext.Provider>
  );
};

ThreeDProvider.displayName = 'ThreeDProvider';