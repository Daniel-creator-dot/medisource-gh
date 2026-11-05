"use client";

export function ThemeToggle() {
  function toggle() {
    const current = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("nova-theme", next);
  }

  return (
    <button type="button" onClick={toggle} className="rounded-full border border-white/25 px-3 py-1 text-sm text-white/80 hover:bg-white/10 hover:text-white">
      Theme
    </button>
  );
}
