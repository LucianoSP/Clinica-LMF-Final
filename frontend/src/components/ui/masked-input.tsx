import { forwardRef } from 'react';
import { Input } from './input';
import { cn } from '@/lib/utils';

interface MaskedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  mask: (value: string) => string;
}

export const MaskedInput = forwardRef<HTMLInputElement, MaskedInputProps>(
  ({ className, mask, value, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const maskedValue = mask(e.target.value);
      e.target.value = maskedValue;
      onChange?.(e);
    };

    return (
      <Input
        ref={ref}
        className={cn(className)}
        value={value}
        onChange={handleChange}
        {...props}
      />
    );
  }
);

MaskedInput.displayName = 'MaskedInput'; 