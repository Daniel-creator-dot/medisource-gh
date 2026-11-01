import type * as React from "react";

import { cn } from "./cn";

export function Card({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("rounded-2xl border border-line bg-white shadow-sm", className)} {...props} />;
}
