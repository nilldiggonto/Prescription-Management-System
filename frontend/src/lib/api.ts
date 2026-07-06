const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface FastApiValidationError {
  loc: (string | number)[];
  msg: string;
}

type FastApiErrorBody = { detail?: string | FastApiValidationError[] };

function extractErrorMessage(body: FastApiErrorBody, fallback: string): string {
  if (!body.detail) return fallback;
  if (typeof body.detail === "string") return body.detail;
  return body.detail.map((error) => error.msg).join(" ");
}

export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

interface ApiFetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  csrf?: boolean;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { body, csrf, headers, ...rest } = options;

  const requestHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string> | undefined),
  };

  if (csrf) {
    const csrfToken = getCsrfToken();
    if (csrfToken) requestHeaders["X-CSRF-Token"] = csrfToken;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: requestHeaders,
    credentials: "include",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new ApiError(response.status, extractErrorMessage(data ?? {}, "Something went wrong. Please try again."));
  }

  return data as T;
}
