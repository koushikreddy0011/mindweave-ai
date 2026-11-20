import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

export const badgeVariants = cva(
  'inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'bg-primary/10 text-primary border border-primary/20',
        navy: 'bg-brand-navy text-white',
        blue: 'bg-blue-50 text-brand-blue border border-blue-200',
        purple: 'bg-purple-50 text-brand-purple border border-purple-200',
        secondary: 'bg-secondary/10 text-secondary border border-secondary/20',
        destructive: 'bg-red-50 text-red-700 border border-red-200',
        outline: 'text-slate-700 border border-slate-300',
        generating: 'bg-amber-50 text-amber-700 border border-amber-300 animate-pulse',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps): React.JSX.Element {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
