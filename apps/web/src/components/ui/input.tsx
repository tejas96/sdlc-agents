import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const inputVariants = cva(
  'flex w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'border-border hover:border-primary/50',
        glass: 'glass border-glass-border hover:border-primary/50',
        outline: 'border-2 border-border hover:border-primary',
      },
      size: {
        default: 'h-10',
        sm: 'h-8 text-xs',
        lg: 'h-12 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  error?: string;
  label?: string;
  description?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    variant, 
    size, 
    type, 
    leftIcon, 
    rightIcon, 
    error, 
    label, 
    description,
    id,
    ...props 
  }, ref) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={inputId}
            className="text-sm font-medium text-foreground mb-2 block"
          >
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}
          
          <input
            id={inputId}
            type={type}
            className={cn(
              inputVariants({ variant, size }),
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-error focus-visible:ring-error',
              className
            )}
            ref={ref}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
              {rightIcon}
            </div>
          )}
        </div>
        
        {description && !error && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
        
        {error && (
          <p className="text-xs text-error mt-1">
            {error}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

// Textarea component
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
  label?: string;
  description?: string;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, label, description, id, ...props }, ref) => {
    const generatedId = React.useId();
    const textareaId = id || generatedId;

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={textareaId}
            className="text-sm font-medium text-foreground mb-2 block"
          >
            {label}
          </label>
        )}
        
        <textarea
          id={textareaId}
          className={cn(
            'flex min-h-[80px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 resize-none',
            error && 'border-error focus-visible:ring-error',
            className
          )}
          ref={ref}
          {...props}
        />
        
        {description && !error && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
        
        {error && (
          <p className="text-xs text-error mt-1">
            {error}
          </p>
        )}
      </div>
    );
  }
);
Textarea.displayName = 'Textarea';

// Search Input component
export interface SearchInputProps extends Omit<InputProps, 'leftIcon' | 'type'> {
  onSearch?: (value: string) => void;
  onClear?: () => void;
  loading?: boolean;
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  ({ onSearch, onClear, loading, className, ...props }, ref) => {
    const [value, setValue] = React.useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      setValue(newValue);
      onSearch?.(newValue);
    };

    const handleClear = () => {
      setValue('');
      onSearch?.('');
      onClear?.();
    };

    return (
      <Input
        ref={ref}
        type="text"
        value={value}
        onChange={handleChange}
        leftIcon={
          loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
          ) : (
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          )
        }
        rightIcon={
          value ? (
            <button
              type="button"
              onClick={handleClear}
              className="hover:text-foreground transition-colors"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          ) : null
        }
        placeholder="Search..."
        className={className}
        {...props}
      />
    );
  }
);
SearchInput.displayName = 'SearchInput';

export { Input, Textarea, SearchInput, inputVariants };
