import { Card } from "@medisource/ui";

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <Card className="px-6 py-12 text-center">
      <h2 className="text-lg font-semibold text-navy">{title}</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-muted">{body}</p>
    </Card>
  );
}

export function ErrorState({ title, body }: { title: string; body: string }) {
  return (
    <Card className="border-danger/20 bg-red-50 px-6 py-8">
      <h2 className="text-lg font-semibold text-danger">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-ink">{body}</p>
    </Card>
  );
}

export function SkeletonGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="h-48 animate-pulse rounded-2xl bg-white" />
      ))}
    </div>
  );
}
