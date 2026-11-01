import type { ApiErrorBody, Envelope, SessionPayload, User } from "@medisource/shared-types";

export class MediSourceApiError extends Error {
  status: number;
  code: string;
  details: unknown;

  constructor(message: string, status: number, code: string, details: unknown = null) {
    super(message);
    this.name = "MediSourceApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  cookie?: string;
  csrfToken?: string;
  client?: "web" | "mobile";
};

export function apiBaseUrl(): string {
  if (typeof window === "undefined") {
    return process.env.API_URL_INTERNAL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.cookie) {
    headers.cookie = options.cookie;
  }
  if (options.csrfToken) {
    headers["X-CSRFToken"] = options.csrfToken;
  }
  if (options.client === "mobile") {
    headers["X-Client"] = "mobile";
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      method: options.method ?? (options.body !== undefined ? "POST" : "GET"),
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      credentials: typeof window === "undefined" ? "omit" : "include",
      cache: "no-store",
    });
  } catch {
    throw new MediSourceApiError("The MediSource API is not reachable.", 0, "network_error");
  }

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as T | ApiErrorBody) : null;
  if (!response.ok) {
    const error = (payload as ApiErrorBody | null)?.error;
    throw new MediSourceApiError(
      error?.message || "Request could not be completed.",
      response.status,
      error?.code || "error",
      error?.details ?? null,
    );
  }
  return payload as T;
}

export class MediSourceClient {
  private csrfToken: string | null = null;

  private async csrf(): Promise<string> {
    if (this.csrfToken) {
      return this.csrfToken;
    }
    const result = await apiRequest<Envelope<{ csrf_token: string }>>("/api/v1/auth/csrf/");
    this.csrfToken = result.data.csrf_token;
    return this.csrfToken;
  }

  private async mutate<T>(path: string, body?: unknown): Promise<T> {
    const csrfToken = await this.csrf();
    try {
      return await apiRequest<T>(path, { method: "POST", body: body ?? {}, csrfToken });
    } catch (error) {
      if (error instanceof MediSourceApiError && error.code === "csrf_failed") {
        this.csrfToken = null;
      }
      throw error;
    }
  }

  login(email: string, password: string) {
    return this.mutate<Envelope<SessionPayload>>("/api/v1/auth/login/", { email, password });
  }

  register(input: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
  }) {
    return this.mutate<Envelope<SessionPayload>>("/api/v1/auth/register/", input);
  }

  verifyMfa(mfaToken: string, code: string) {
    return this.mutate<Envelope<SessionPayload>>("/api/v1/auth/mfa/verify/", {
      mfa_token: mfaToken,
      code,
    });
  }

  logout() {
    return this.mutate<Envelope<{ logged_out: boolean }>>("/api/v1/auth/logout/", {});
  }

  me() {
    return apiRequest<Envelope<User>>("/api/v1/auth/me/");
  }

  updateMe(input: { first_name?: string; last_name?: string; phone_number?: string }) {
    return this.change<Envelope<User>>("/api/v1/auth/me/", input);
  }

  verifyEmail(token: string) {
    return this.mutate<Envelope<{ email_verified: boolean }>>("/api/v1/auth/verify-email/", { token });
  }

  requestPasswordReset(email: string) {
    return this.mutate<Envelope<{ message: string }>>("/api/v1/auth/password-reset/", { email });
  }

  confirmPasswordReset(token: string, password: string) {
    return this.mutate<Envelope<{ reset: boolean }>>("/api/v1/auth/password-reset/confirm/", {
      token,
      password,
    });
  }

  private async change<T>(path: string, body: unknown): Promise<T> {
    const csrfToken = await this.csrf();
    return apiRequest<T>(path, { method: "PATCH", body, csrfToken });
  }
}
