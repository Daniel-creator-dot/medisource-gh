import { Button } from "@medisource/ui";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center">
      <h1 className="text-3xl font-semibold text-navy">That page is not available</h1>
      <p className="mt-3 text-sm leading-6 text-muted">
        The address may be wrong, or the catalogue record is not public.
      </p>
      <Button asChild className="mt-6">
        <Link href="/shop">Back to the shop</Link>
      </Button>
    </div>
  );
}
