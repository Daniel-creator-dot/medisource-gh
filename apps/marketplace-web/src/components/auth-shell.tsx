import { Card } from "@medisource/ui";
import Link from "next/link";
import { Suspense, type ReactNode } from "react";

export function AuthShell({
  title,
  body,
  children,
  footer,
}: {
  title: string;
  body: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-navy">{title}</h1>
      <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
      <Card className="mt-6 p-6">
        <Suspense fallback={<p className="text-sm text-muted">Loading…</p>}>{children}</Suspense>
      </Card>
      {footer ? <div className="mt-4 text-sm text-muted">{footer}</div> : null}
    </div>
  );
}

export function AuthLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link href={href} className="font-semibold text-teal-dark">
      {children}
    </Link>
  );
}
