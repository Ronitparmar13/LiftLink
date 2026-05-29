import { useEffect, useState } from 'react';

/**
 * Check if 3D rendering is supported and enabled based on device capabilities
 * and user preferences
 */
export function useThreeDCapabilities() {
  const [isSupported, setIsSupported] = useState<boolean>(false);
  const [isEnabled, setIsEnabled] = useState<boolean>(true);

  useEffect(() => {
    // Check if WebGL is supported
    const canvas = document.createElement('canvas');
    setIsSupported(!!(canvas.getContext('webgl2') || canvas.getContext('webgl')));
    
    // Check user preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      setIsEnabled(false);
    }
    
    // Check device memory if available (with fallback for older browsers)
    const mem = (navigator as Navigator & { deviceMemory?: number }).deviceMemory;
    if (mem !== undefined && mem < 0.5) {
      setIsEnabled(false);
    }
  }, []);

  return { isSupported, isEnabled, setIsEnabled };
}