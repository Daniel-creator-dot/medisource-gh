"use client";

import { Button } from "@medisource/ui";

export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="text-3xl font-semibold text-navy">Something went wrong</h1>
      <p className="mt-3 text-sm leading-6 text-muted">The page could not be rendered. You can try again.</p>
      <Button className="mt-6" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
