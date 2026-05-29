import { useState } from 'react';

interface Panel3DProps extends React.HTMLAttributes<HTMLDivElement> {
  elevation?: number; // 1-5
  children: React.ReactNode;
}

const Panel3D = ({
  elevation = 2,
  className,
  children,
  ...props
}: Panel3DProps) => {
  const [isHovered, setIsHovered] = useState(false);
   
  // Calculate transform values based on elevation and hover state
  const baseLift = elevation * 2; // 2px per elevation unit
  const hoverLift = isHovered ? baseLift + 2 : baseLift; // Additional lift on hover
   
  // Shadow classes based on elevation
  const shadowClasses = {
    0: 'shadow-none',
    1: 'shadow-sm',
    2: 'shadow',
    3: 'shadow-md',
    4: 'shadow-lg',
    5: 'shadow-xl',
  }[elevation] || 'shadow';
   
  // Base classes
  const baseClasses = `
    transition-all duration-300 ease-out
    transform-gpu
    rounded-xl
    bg-card
    border border-border
    background-clip-padding
  `;
   
  return (
    <div
      className={`${baseClasses} ${shadowClasses} ${className || ''}`}
      style={{
        transform: `translateZ(0) translateY(${-hoverLift}px)`,
        transition: 'transform 300ms ease-out, box-shadow 300ms ease-out',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      {...props}
    >
      {children}
    </div>
  );
};

Panel3D.displayName = 'Panel3D';

export default Panel3D;