import { createContext } from 'react';

export const ThreeDContext = createContext<{
  isSupported: boolean;
  isEnabled: boolean;
  toggleEnabled: () => void;
} | undefined>(undefined);