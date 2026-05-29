import { forwardRef } from 'react';

interface Button3DProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  elevation?: number; // 1-5
  tiltEnabled?: boolean;
  children: React.ReactNode;
}

const Button3D = forwardRef<HTMLButtonElement, Button3DProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      elevation = 2,
      tiltEnabled = true,
      className,
      children,
      ...props
    },
    ref
  ) => {
    // Calculate transform values based on elevation
    const lift = elevation * 4; // 4px per elevation unit
    const tiltAmount = tiltEnabled ? elevation * 0.5 : 0; // degrees

    // Base classes
    const baseClasses = `
      transition-all duration-200 ease-out
      transform-gpu
      rounded-lg
      font-medium
      flex items-center justify-center
      whitespace-nowrap
    `;

    // Variant classes
    const variantClasses = {
      primary:
        'bg-primary-600 text-primary-50 hover:bg-primary-700 focus:bg-primary-700 focus:ring-2 focus:ring-primary-300',
      secondary:
        'bg-secondary-600 text-secondary-50 hover:bg-secondary-700 focus:bg-secondary-700 focus:ring-2 focus:ring-secondary-300',
      outline:
        'border border-primary-600 text-primary-600 hover:bg-primary-50 focus:bg-primary-50 focus:ring-2 focus:ring-primary-300',
    }[variant];

    // Size classes
    const sizeClasses = {
      sm: 'h-9 px-3 text-sm',
      md: 'h-10 px-4 text-base',
      lg: 'h-12 px-5 text-lg',
    }[size];

    // Shadow classes based on elevation
    const shadowClasses = {
      0: 'shadow-none',
      1: 'shadow-sm',
      2: 'shadow',
      3: 'shadow-md',
      4: 'shadow-lg',
      5: 'shadow-xl',
    }[elevation] || 'shadow';

    // Hover transform: lift up and tilt
    const hoverTransform = `
      translate-y-[-${lift}px]
      rotate-x-[${tiltAmount}deg]
      rotate-y-[${tiltAmount}deg]
      scale-102
    `;

    // Press transform: push down
    const pressTransform = `
      translate-y-[${lift / 2}px]
      rotate-x-[-${tiltAmount / 2}deg]
      rotate-y-[-${tiltAmount / 2}deg]
      scale-98
    `;

    return (
      <button
        ref={ref}
        className={`${baseClasses} ${variantClasses} ${sizeClasses} ${shadowClasses} ${className || ''}`}
        style={{
          transform: 'translateZ(0)', // Ensure GPU acceleration
          transition: 'transform 200ms ease-out, box-shadow 200ms ease-out',
        }}
        onMouseEnter={(e) => {
          if (tiltEnabled) {
            // Calculate tilt based on cursor position
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            const tiltX = deltaY * tiltAmount * 2; // Reverse Y for natural tilt
            const tiltY = deltaX * tiltAmount * 2;
            e.currentTarget.style.transform = `
              translate-y-[-${lift}px]
              rotate-x-[${tiltX}deg]
              rotate-y-[${tiltY}deg]
              scale-102
            `;
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = '';
        }}
        onMouseDown={(e) => {
          e.currentTarget.style.transform = pressTransform;
        }}
        onMouseUp={(e) => {
          if (tiltEnabled) {
            // Calculate tilt based on cursor position on up
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            const tiltX = deltaY * tiltAmount * 2;
            const tiltY = deltaX * tiltAmount * 2;
            e.currentTarget.style.transform = `
              translate-y-[-${lift}px]
              rotate-x-[${tiltX}deg]
              rotate-y-[${tiltY}deg]
              scale-102
            `;
          } else {
            e.currentTarget.style.transform = hoverTransform;
          }
        }}
        onDragStart={(e) => e.preventDefault()} // Prevent drag interference
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button3D.displayName = 'Button3D';

export default Button3D;