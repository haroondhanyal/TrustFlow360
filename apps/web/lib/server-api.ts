import { cookies } from "next/headers";

const apiOrigin = process.env.API_URL ?? "http://localhost:8000";

export async function serverApi<T = Record<string, unknown>>(path: string): Promise<T | null> {
  const token = (await cookies()).get("tf_access")?.value;
  if (!token) return null;
  try {
    const response = await fetch(`${apiOrigin}${path}`, { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
    if (!response.ok) return null;
    return await response.json() as T;
  } catch { return null; }
}
