"use client";

import { Button } from "@medisource/ui";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { browserApi } from "@/lib/browser-api";

export function AccountNav() {
  const session = useQuery({ queryKey: ["me"], queryFn: () => browserApi.me(), retry: false });
  if (session.isPending) {
    return <div className="h-9 w-24" aria-hidden="true" />;
  }
  if (session.data) {
    return (
      <Button asChild size="sm">
        <Link href="/account/dashboard">Account</Link>
      </Button>
    );
  }
  return (
    <>
      <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
        <Link href="/login">Sign in</Link>
      </Button>
      <Button asChild size="sm">
        <Link href="/register">Create account</Link>
      </Button>
    </>
  );
}
