import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const api = process.env.API_URL || "http://127.0.0.1:8010";

export type ApiResult<T> = { status: number; data: T | null; message: string | null };

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  const jar = await cookies();
  let response: Response;
  try {
    response = await fetch(`${api}/api/v1${path}`, {
      headers: { cookie: jar.toString() },
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
  } catch {
    return { status: 503, data: null, message: "The API did not answer. Wait a moment and try again." };
  }
  if (response.status === 401) redirect("/");
  const text = await response.text();
  try {
    const body = (text ? JSON.parse(text) : {}) as { data?: T; error?: { message?: string } };
    return { status: response.status, data: body.data ?? null, message: body.error?.message ?? null };
  } catch {
    return { status: response.status, data: null, message: "The API returned a page instead of data." };
  }
}
