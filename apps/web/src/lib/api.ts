import type {
  ApiError,
  HealthResponse,
  Language,
  LessonSummary,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  TranslationRequest,
  TranslationResponse,
  User,
} from "@/types";

/**
 * Base URL of the API.
 * - Server components (SSR, inside Docker) use API_INTERNAL_URL (e.g. http://api:8000).
 * - The browser uses NEXT_PUBLIC_API_URL (e.g. http://localhost:8000).
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: ApiError | null,
  ) {
    super(`API request failed with status ${status}`);
    this.name = "ApiRequestError";
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  token?: string;
}

export async function apiFetch<T>(path: string, { body, token, headers, ...init }: RequestOptions = {}): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const errorBody = (await res.json().catch(() => null)) as ApiError | null;
    throw new ApiRequestError(res.status, errorBody);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => apiFetch<HealthResponse>("/health", { cache: "no-store" }),
  languages: () => apiFetch<Language[]>("/api/v1/languages"),
  lessons: (params: { language?: string; level?: string } = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => Boolean(v)) as [string, string][]);
    return apiFetch<LessonSummary[]>(`/api/v1/lessons${qs.size ? `?${qs}` : ""}`);
  },
  register: (data: RegisterRequest) => apiFetch<User>("/api/v1/auth/register", { method: "POST", body: data }),
  login: (data: LoginRequest) => apiFetch<TokenResponse>("/api/v1/auth/login", { method: "POST", body: data }),
  me: (token: string) => apiFetch<User>("/api/v1/users/me", { token }),
  translate: (data: TranslationRequest, token: string) =>
    apiFetch<TranslationResponse>("/api/v1/translate", { method: "POST", body: data, token }),
};
