import { NextRequest, NextResponse } from "next/server";

const apiOrigin = process.env.API_URL ?? "http://localhost:8000";
const accessAge = 15 * 60;
const refreshAge = 14 * 24 * 60 * 60;

export async function POST(request: NextRequest, context: { params: Promise<{ action: string }> }) {
  const { action } = await context.params;
  if (!["login", "register", "refresh", "logout"].includes(action)) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const body = action === "refresh" || action === "logout"
    ? { refresh_token: request.cookies.get("tf_refresh")?.value ?? "" }
    : await request.json();
  let upstream: Response;
  try {
    upstream = await fetch(`${apiOrigin}/auth/${action}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store" });
  } catch {
    return NextResponse.json({ detail: "TrustFlow services are unavailable. Start the API and database, then try again." }, { status: 503 });
  }
  if (action === "logout") {
    const response = NextResponse.json({ ok: true }, { status: 200 });
    response.cookies.set("tf_access", "", { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 0 });
    response.cookies.set("tf_refresh", "", { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 0 });
    response.cookies.set("tf_remember", "", { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 0 });
    return response;
  }
  const result = await upstream.json();
  if (!upstream.ok) return NextResponse.json(result, { status: upstream.status });
  const response = NextResponse.json({ user: result.user, organization: result.organization, has_organization: Boolean(result.organization) }, { status: upstream.status });
  const remembered = body.remember === true;
  response.cookies.set("tf_access", result.access_token, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: accessAge });
  response.cookies.set("tf_refresh", result.refresh_token, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: remembered ? refreshAge : 12 * 60 * 60 });
  response.cookies.set("tf_remember", remembered ? "1" : "0", { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: remembered ? refreshAge : 12 * 60 * 60 });
  return response;
}
