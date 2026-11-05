import { NextRequest, NextResponse } from "next/server";

const api = process.env.API_URL || "http://127.0.0.1:8010";

export const dynamic = "force-dynamic";

const forwarded = ["cookie", "content-type", "x-csrftoken", "authorization", "origin", "accept"];

function unavailable() {
  return NextResponse.json(
    { error: { code: "unavailable", message: "The API did not answer. Wait a moment and try again.", details: null } },
    { status: 503 },
  );
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(`${api}/api/v1/${path.filter(Boolean).join("/")}/`);
  target.search = request.nextUrl.search;
  const headers = new Headers();
  for (const name of forwarded) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  try {
    const response = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.arrayBuffer(),
      redirect: "manual",
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
    const text = await response.text();
    const type = response.headers.get("content-type") || "";
    const payload = type.includes("application/json")
      ? text || "{}"
      : JSON.stringify({
          error: { code: "bad_gateway", message: "The API returned a page instead of data.", details: null },
        });
    const status = type.includes("application/json") ? response.status : 502;
    const outgoing = new NextResponse(payload, { status, headers: { "content-type": "application/json" } });
    for (const cookie of response.headers.getSetCookie()) outgoing.headers.append("set-cookie", cookie);
    return outgoing;
  } catch {
    return unavailable();
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
