 // Base URL of the local FastAPI backend.
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

// Reusable API helper for requests that return JSON.
export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  // Send JSON requests to FastAPI.
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  // Read the response body so we can display useful API error messages.
  const body = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = body?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : `API request failed (${response.status})`;

    throw new Error(message);
  }

  // Handle endpoints that return 204 No Content, such as DELETE.
  if (response.status === 204) {
    return undefined as T;
  }

  return body as T;
}

// Convenient wrapper for GET requests.
export function getJson<T>(path: string): Promise<T> {
  return apiRequest<T>(path);
}

// Convenient wrapper for POST requests that send JSON.
export function postJson<T, B>(path: string, data: B): Promise<T> {
  return apiRequest<T>(path, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
