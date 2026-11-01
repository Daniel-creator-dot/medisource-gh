import * as React from "react";

import { cn } from "./cn";

export const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(function Input(
  { className, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      className={cn(
        "h-11 w-full rounded-xl border border-line bg-white px-3 text-sm text-ink outline-none placeholder:text-muted/70 focus-visible:ring-2 focus-visible:ring-teal",
        className,
      )}
      {...props}
    />
  );
});

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.ComponentProps<"textarea">>(
  function Textarea({ className, ...props }, ref) {
    return (
      <textarea
        ref={ref}
        className={cn(
          "min-h-32 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm text-ink outline-none placeholder:text-muted/70 focus-visible:ring-2 focus-visible:ring-teal",
          className,
        )}
        {...props}
      />
    );
  },
);

export function Label({ className, ...props }: React.ComponentProps<"label">) {
  return <label className={cn("text-sm font-medium text-navy", className)} {...props} />;
}
