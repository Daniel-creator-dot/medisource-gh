export async function register() {
  if (process.env.NEXT_RUNTIME !== "nodejs") return;
  const api = process.env.API_URL;
  if (!api || api.includes("127.0.0.1") || api.includes("localhost")) return;

  const wake = () => {
    fetch(`${api}/api/v1/health/`, { cache: "no-store", signal: AbortSignal.timeout(70000) }).catch(() => undefined);
  };
  wake();
  const timer = setInterval(wake, 4 * 60 * 1000);
  timer.unref();
}
