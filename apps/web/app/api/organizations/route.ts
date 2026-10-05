import { NextRequest, NextResponse } from "next/server";

const apiOrigin = process.env.API_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const access = request.cookies.get("tf_access")?.value;
  if (!access) return NextResponse.json({ detail: "Your session expired. Sign in and try again." }, { status: 401 });
  let upstream: Response;
  try {
    upstream = await fetch(`${apiOrigin}/organizations`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${access}` }, body: await request.text(), cache: "no-store" });
  } catch {
    return NextResponse.json({ detail: "TrustFlow services are unavailable. Start the API and database, then try again." }, { status: 503 });
  }
  const result = await upstream.json();
  if (!upstream.ok) return NextResponse.json(result, { status: upstream.status });
  const response = NextResponse.json({ organization: result.organization }, { status: upstream.status });
  response.cookies.set("tf_access", result.access_token, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: 15 * 60 });
  return response;
}
