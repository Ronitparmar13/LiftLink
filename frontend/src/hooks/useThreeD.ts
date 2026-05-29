import { useContext } from 'react';
import { ThreeDContext } from '@/contexts/ThreeDContext';

/**
 * Hook to access the 3D context
 * Must be used within a ThreeDProvider
 */
export function useThreeD() {
  const context = useContext(ThreeDContext);
  if (context === undefined) {
    throw new Error('useThreeD must be used within a ThreeDProvider');
  }
  return context;
}