import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const access = request.cookies.get("tf_access")?.value;
  if ((!access || expiresSoon(access)) && request.cookies.has("tf_refresh")) {
    return refreshAndContinue(request);
  }
  if (!request.cookies.has("tf_access")) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

function expiresSoon(token: string) {
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const claims = JSON.parse(atob(payload));
    return typeof claims.exp === "number" && claims.exp * 1000 < Date.now() + 60_000;
  } catch { return true; }
}

async function refreshAndContinue(request: NextRequest) {
  const origin = process.env.API_URL ?? "http://localhost:8000";
  try {
    const response = await fetch(`${origin}/auth/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: request.cookies.get("tf_refresh")?.value }), cache: "no-store" });
    if (response.ok) {
      const tokens = await response.json();
      const next = NextResponse.redirect(request.nextUrl);
      const secure = process.env.NODE_ENV === "production";
      next.cookies.set("tf_access", tokens.access_token, { httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: 15 * 60 });
      const remember = request.cookies.get("tf_remember")?.value === "1";
      next.cookies.set("tf_refresh", tokens.refresh_token, { httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: remember ? 14 * 24 * 60 * 60 : 12 * 60 * 60 });
      return next;
    }
  } catch { /* The protected page will report the unavailable API. */ }
  const login = new URL("/login", request.url);
  login.searchParams.set("next", request.nextUrl.pathname);
  const response = NextResponse.redirect(login);
  response.cookies.delete("tf_access");
  response.cookies.delete("tf_refresh");
  response.cookies.delete("tf_remember");
  return response;
}

export const config = { matcher: ["/dashboard/:path*", "/profile/:path*", "/vendors/:path*", "/organization/:path*", "/rfqs/:path*", "/bids/:path*", "/approvals/:path*", "/contracts/:path*", "/purchase-orders/:path*", "/shipments/:path*", "/finance/:path*", "/risks/:path*", "/credentials/:path*", "/assets/:path*", "/proofs/:path*", "/assistant/:path*", "/verify/:path*"] };
