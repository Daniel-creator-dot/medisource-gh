import type * as React from "react";

import { cn } from "./cn";

const tones = {
  sample: "bg-amber-50 text-warning",
  neutral: "bg-canvas text-navy",
  closed: "bg-red-50 text-danger",
  open: "bg-emerald-50 text-success",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: React.ComponentProps<"span"> & { tone?: keyof typeof tones }) {
  return (
    <span
      className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", tones[tone], className)}
      {...props}
    />
  );
}
