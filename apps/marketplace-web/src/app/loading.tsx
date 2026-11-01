import { SkeletonGrid } from "@/components/states";

export default function Loading() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16">
      <SkeletonGrid />
    </div>
  );
}
