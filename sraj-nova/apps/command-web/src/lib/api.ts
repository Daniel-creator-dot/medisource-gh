import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const api = process.env.API_URL || "http://127.0.0.1:8010";

export type ApiResult<T> = { status: number; data: T | null; message: string | null };

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  const jar = await cookies();
  const response = await fetch(`${api}/api/v1${path}`, {
    headers: { cookie: jar.toString() },
    cache: "no-store",
  });
  const body = (await response.json()) as { data?: T; error?: { message?: string } };
  if (response.status === 401) redirect("/login");
  return { status: response.status, data: body.data ?? null, message: body.error?.message ?? null };
}
