"use client";

export function ThemeToggle() {
  function toggle() {
    const current = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("nova-theme", next);
  }

  return (
    <button type="button" onClick={toggle} className="w-full rounded-2xl bg-[var(--canvas)] px-3 py-2 text-left text-sm font-semibold text-[var(--ink)]">
      Theme
    </button>
  );
}
