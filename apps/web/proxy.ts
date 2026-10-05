import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  if (!request.cookies.has("tf_access")) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*"] };
