import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { Button } from './button';

const cardVariants = cva(
  'rounded-lg border text-foreground shadow-sm transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'bg-background border-border',
        glass: 'glass border-glass-border backdrop-blur-md',
        elevated: 'bg-background border-border shadow-lg hover:shadow-xl',
        outline: 'bg-transparent border-border',
        gradient: 'bg-gradient-to-br from-background to-muted border-border',
      },
      size: {
        default: 'p-6',
        sm: 'p-4',
        lg: 'p-8',
        xl: 'p-10',
      },
      hover: {
        none: '',
        lift: 'hover:scale-[1.02] hover:shadow-lg',
        glow: 'hover:shadow-lg hover:shadow-primary/20',
        border: 'hover:border-primary/50',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      hover: 'none',
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, hover, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size, hover, className }))}
      {...props}
    />
  )
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight',
      className
    )}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

// Specialized card components for the SDLC Agents app
export interface StatCardProps extends CardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ 
    title, 
    value, 
    description, 
    icon, 
    trend, 
    color = 'primary',
    className,
    ...props 
  }, ref) => {
    const colorClasses = {
      primary: 'border-primary/20 bg-primary/5',
      secondary: 'border-secondary/20 bg-secondary/5',
      success: 'border-success/20 bg-success/5',
      warning: 'border-warning/20 bg-warning/5',
      error: 'border-error/20 bg-error/5',
    };

    const iconColorClasses = {
      primary: 'text-primary bg-primary/10',
      secondary: 'text-secondary bg-secondary/10',
      success: 'text-success bg-success/10',
      warning: 'text-warning bg-warning/10',
      error: 'text-error bg-error/10',
    };

    return (
      <Card
        ref={ref}
        variant="glass"
        hover="lift"
        className={cn(colorClasses[color], className)}
        {...props}
      >
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground mb-2">
                {title}
              </p>
              <div className="flex items-baseline space-x-2">
                <p className="text-3xl font-bold text-foreground">
                  {value}
                </p>
                {trend && (
                  <span
                    className={cn(
                      'text-sm font-medium px-2 py-1 rounded-full',
                      trend.isPositive
                        ? 'text-success bg-success/10'
                        : 'text-error bg-error/10'
                    )}
                  >
                    {trend.isPositive ? '+' : ''}{trend.value}%
                  </span>
                )}
              </div>
              {description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {description}
                </p>
              )}
            </div>
            {icon && (
              <div className={cn(
                'w-12 h-12 rounded-lg flex items-center justify-center',
                iconColorClasses[color]
              )}>
                {icon}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }
);
StatCard.displayName = 'StatCard';

export interface AgentCardProps extends CardProps {
  agent: {
    id: number;
    name: string;
    description?: string;
    status: string;
    agent_type: string;
    total_executions: number;
    successful_executions: number;
    last_execution_at?: string;
  };
  onExecute?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

const AgentCard = React.forwardRef<HTMLDivElement, AgentCardProps>(
  ({ agent, onExecute, onEdit, onDelete, className, ...props }, ref) => {
    const successRate = agent.total_executions > 0 
      ? Math.round((agent.successful_executions / agent.total_executions) * 100)
      : 0;

    const statusColors = {
      active: 'text-success bg-success/10',
      inactive: 'text-muted-foreground bg-muted/10',
      paused: 'text-warning bg-warning/10',
      error: 'text-error bg-error/10',
      maintenance: 'text-warning bg-warning/10',
    };

    return (
      <Card
        ref={ref}
        variant="glass"
        hover="lift"
        className={cn('relative overflow-hidden', className)}
        {...props}
      >
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
        
        <CardHeader className="relative">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-lg">{agent.name}</CardTitle>
              <CardDescription className="mt-1">
                {agent.description || `${agent.agent_type.replace('_', ' ')} agent`}
              </CardDescription>
            </div>
            <span
              className={cn(
                'px-2 py-1 text-xs font-medium rounded-full',
                statusColors[agent.status as keyof typeof statusColors] || statusColors.inactive
              )}
            >
              {agent.status}
            </span>
          </div>
        </CardHeader>

        <CardContent className="relative">
          <div className="flex items-center justify-between text-sm">
            <div className="text-center">
              <p className="font-semibold text-lg">{successRate}%</p>
              <p className="text-muted-foreground">Success Rate</p>
            </div>
            <div className="text-center">
              <p className="font-semibold text-lg">{agent.total_executions}</p>
              <p className="text-muted-foreground">Executions</p>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Performance</span>
              <span>{successRate}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all duration-300"
                style={{ width: `${successRate}%` }}
              />
            </div>
          </div>
        </CardContent>

        <CardFooter className="relative flex justify-between">
          <div className="flex space-x-2">
            {onExecute && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onExecute(agent.id)}
                disabled={agent.status !== 'active'}
              >
                Execute
              </Button>
            )}
            {onEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(agent.id)}
              >
                Edit
              </Button>
            )}
          </div>
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(agent.id)}
              className="text-error hover:text-error"
            >
              Delete
            </Button>
          )}
        </CardFooter>
      </Card>
    );
  }
);
AgentCard.displayName = 'AgentCard';

export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent,
  StatCard,
  AgentCard,
  cardVariants 
};
