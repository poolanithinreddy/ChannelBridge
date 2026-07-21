const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
export const getToken = () => localStorage.getItem("cb_token");
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (getToken()) headers.set("Authorization", `Bearer ${getToken()}`);
  if (init.body && !(init.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : body.detail?.message || "Request failed",
    );
  }
  return res.json();
}
export async function login(email: string, password: string) {
  const value = await api<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("cb_token", value.access_token);
  return value;
}
export { BASE };
