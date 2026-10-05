"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowRight } from "lucide-react";

export function JoinForm() {
  const params = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(form: FormData) {
    setError(""); setBusy(true);
    const email = String(form.get("email"));
    const password = String(form.get("password"));
    try {
      const response = await fetch("/api/backend/organization/invitations/accept", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token: params.get("token"), email, first_name: form.get("first_name"), last_name: form.get("last_name"), password }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "The invitation could not be accepted.");
      const login = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
      if (!login.ok) throw new Error("Your account was created. Sign in to open the workspace.");
      router.push("/dashboard"); router.refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not join this workspace."); }
    finally { setBusy(false); }
  }

  return <form action={submit} className="form-fields"><div className="name-fields"><label>First name<input name="first_name" required autoComplete="given-name"/></label><label>Last name<input name="last_name" required autoComplete="family-name"/></label></div><label>Work email<input name="email" type="email" required autoComplete="email" placeholder="Use the address your teammate invited"/></label><label>Create password<input name="password" type="password" required minLength={10} autoComplete="new-password" placeholder="At least 10 characters"/></label>{error&&<p className="form-error" role="alert">{error}</p>}<button className="button form-submit" disabled={busy}>{busy?"Joining…":<>Accept invitation <ArrowRight size={17}/></>}</button><p className="form-bottom"><Link href="/login">Already joined? Sign in</Link></p></form>;
}
