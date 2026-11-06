"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

const pages = [
  ["command", "/command"],
  ["action", "/work"],
  ["floor", "/floor"],
  ["department", "/departments"],
  ["coverage", "/deployment"],
  ["people", "/employees"],
  ["employee", "/employees"],
  ["finance", "/finance"],
  ["book", "/accounting"],
  ["invoice", "/finance"],
  ["client", "/clients"],
  ["agency", "/agency"],
  ["access", "/access"],
  ["record", "/me"],
] as const;

export function WorkspaceSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  return (
    <form
      className="search"
      onSubmit={(event) => {
        event.preventDefault();
        const needle = query.trim().toLowerCase();
        const match = pages.find(([label]) => label.includes(needle) || needle.includes(label));
        if (match) router.push(match[1]);
      }}
    >
      <Search aria-hidden="true" size={16} />
      <label className="sr-only" htmlFor="workspace-search">Search pages</label>
      <input id="workspace-search" placeholder="Search pages" value={query} onChange={(event) => setQuery(event.target.value)} />
    </form>
  );
}
