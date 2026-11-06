"use client";

export function ThemeToggle() {
  function toggle() {
    const current = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("nova-theme", next);
  }

  return (
    <button type="button" onClick={toggle} className="w-full rounded-xl border border-white/20 px-3 py-2 text-left text-sm text-white/80 hover:bg-white/10">
      Theme
    </button>
  );
}
