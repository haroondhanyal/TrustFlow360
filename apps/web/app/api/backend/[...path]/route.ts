import { NextRequest, NextResponse } from "next/server";

const apiOrigin = process.env.API_URL ?? "http://localhost:8000";
const allowedRoots = new Set(["vendors", "rfqs", "bids", "approvals", "contracts", "purchase-orders", "organization", "operations"]);
const publicPaths = new Set(["organization/invitations/accept"]);

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const apiPath = path.join("/");
  if (!allowedRoots.has(path[0]) || path.some((part) => part === "..")) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const access = request.cookies.get("tf_access")?.value;
  if (!access && !publicPaths.has(apiPath)) return NextResponse.json({ detail: "Sign in to continue" }, { status: 401 });

  const headers = new Headers();
  if (access) headers.set("Authorization", `Bearer ${access}`);
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);
  const method = request.method;
  const body = method === "GET" || method === "HEAD" ? undefined : await request.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${apiOrigin}/${apiPath}${request.nextUrl.search}`, { method, headers, body, cache: "no-store" });
  } catch {
    return NextResponse.json({ detail: "TrustFlow services are unavailable. Start the API and database, then try again." }, { status: 503 });
  }
  if (upstream.status === 204) return new NextResponse(null, { status: 204 });
  return NextResponse.json(await upstream.json(), { status: upstream.status });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
