import * as React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { Button } from './button';

const modalVariants = cva(
  'fixed left-[50%] top-[50%] z-50 w-full translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg',
  {
    variants: {
      size: {
        default: 'max-w-lg',
        sm: 'max-w-md',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl',
        full: 'max-w-[95vw] max-h-[95vh]',
      },
      variant: {
        default: 'border-border',
        glass: 'glass border-glass-border backdrop-blur-md',
      },
    },
    defaultVariants: {
      size: 'default',
      variant: 'default',
    },
  }
);

export interface ModalProps
  extends React.ComponentPropsWithoutRef<typeof Dialog.Content>,
    VariantProps<typeof modalVariants> {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const Modal = React.forwardRef<
  React.ElementRef<typeof Dialog.Content>,
  ModalProps
>(({ className, size, variant, children, ...props }, ref) => (
  <Dialog.Content
    ref={ref}
    className={cn(modalVariants({ size, variant, className }))}
    {...props}
  >
    {children}
  </Dialog.Content>
));
Modal.displayName = Dialog.Content.displayName;

const ModalTrigger = Dialog.Trigger;

const ModalPortal = Dialog.Portal;

const ModalOverlay = React.forwardRef<
  React.ElementRef<typeof Dialog.Overlay>,
  React.ComponentPropsWithoutRef<typeof Dialog.Overlay>
>(({ className, ...props }, ref) => (
  <Dialog.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      className
    )}
    {...props}
  />
));
ModalOverlay.displayName = Dialog.Overlay.displayName;

const ModalHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      'flex flex-col space-y-1.5 text-center sm:text-left',
      className
    )}
    {...props}
  />
);
ModalHeader.displayName = 'ModalHeader';

const ModalFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      'flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2',
      className
    )}
    {...props}
  />
);
ModalFooter.displayName = 'ModalFooter';

const ModalTitle = React.forwardRef<
  React.ElementRef<typeof Dialog.Title>,
  React.ComponentPropsWithoutRef<typeof Dialog.Title>
>(({ className, ...props }, ref) => (
  <Dialog.Title
    ref={ref}
    className={cn(
      'text-lg font-semibold leading-none tracking-tight',
      className
    )}
    {...props}
  />
));
ModalTitle.displayName = Dialog.Title.displayName;

const ModalDescription = React.forwardRef<
  React.ElementRef<typeof Dialog.Description>,
  React.ComponentPropsWithoutRef<typeof Dialog.Description>
>(({ className, ...props }, ref) => (
  <Dialog.Description
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
));
ModalDescription.displayName = Dialog.Description.displayName;

const ModalClose = React.forwardRef<
  React.ElementRef<typeof Dialog.Close>,
  React.ComponentPropsWithoutRef<typeof Dialog.Close>
>(({ className, ...props }, ref) => (
  <Dialog.Close
    ref={ref}
    className={cn(
      'absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-muted data-[state=open]:text-muted-foreground',
      className
    )}
    {...props}
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
    <span className="sr-only">Close</span>
  </Dialog.Close>
));
ModalClose.displayName = Dialog.Close.displayName;

// Complete Modal wrapper component
export interface ModalWrapperProps extends ModalProps {
  trigger?: React.ReactNode;
  title?: string;
  description?: string;
  showClose?: boolean;
}

const ModalWrapper: React.FC<ModalWrapperProps> = ({
  trigger,
  title,
  description,
  showClose = true,
  children,
  open,
  onOpenChange,
  ...props
}) => (
  <Dialog.Root open={open} onOpenChange={onOpenChange}>
    {trigger && <ModalTrigger asChild>{trigger}</ModalTrigger>}
    <ModalPortal>
      <ModalOverlay />
      <Modal {...props}>
        {showClose && <ModalClose />}
        {(title || description) && (
          <ModalHeader>
            {title && <ModalTitle>{title}</ModalTitle>}
            {description && <ModalDescription>{description}</ModalDescription>}
          </ModalHeader>
        )}
        {children}
      </Modal>
    </ModalPortal>
  </Dialog.Root>
);

// Confirmation Modal
export interface ConfirmModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  loading?: boolean;
  variant?: 'default' | 'destructive';
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({
  open,
  onOpenChange,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  loading = false,
  variant = 'default',
}) => {
  const handleConfirm = () => {
    onConfirm();
  };

  const handleCancel = () => {
    onCancel?.();
    onOpenChange(false);
  };

  return (
    <ModalWrapper
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      size="sm"
      variant="glass"
    >
      <ModalFooter className="mt-6">
        <Button
          variant="ghost"
          onClick={handleCancel}
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          variant={variant === 'destructive' ? 'destructive' : 'default'}
          onClick={handleConfirm}
          loading={loading}
          disabled={loading}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </ModalWrapper>
  );
};

// Form Modal
export interface FormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  onSubmit?: (e: React.FormEvent) => void;
  submitText?: string;
  cancelText?: string;
  loading?: boolean;
  submitDisabled?: boolean;
}

const FormModal: React.FC<FormModalProps> = ({
  open,
  onOpenChange,
  title,
  description,
  children,
  onSubmit,
  submitText = 'Save',
  cancelText = 'Cancel',
  loading = false,
  submitDisabled = false,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(e);
  };

  return (
    <ModalWrapper
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      variant="glass"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="py-4">
          {children}
        </div>
        <ModalFooter>
          <Button
            type="button"
            variant="ghost"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            {cancelText}
          </Button>
          <Button
            type="submit"
            loading={loading}
            disabled={loading || submitDisabled}
          >
            {submitText}
          </Button>
        </ModalFooter>
      </form>
    </ModalWrapper>
  );
};

export {
  Modal,
  ModalTrigger,
  ModalPortal,
  ModalOverlay,
  ModalHeader,
  ModalFooter,
  ModalTitle,
  ModalDescription,
  ModalClose,
  ModalWrapper,
  ConfirmModal,
  FormModal,
};
