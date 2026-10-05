"use client";

import { useState } from "react";
import { ArrowRight, Eye, EyeOff } from "lucide-react";

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(form: FormData) {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.get("email"), password: form.get("password"), remember: Boolean(form.get("remember")) }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "We could not sign you in. Check your details and try again.");
      window.location.assign(result.has_organization ? "/dashboard" : "/signup?step=organization");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The service is unavailable. Try again shortly.");
    } finally { setBusy(false); }
  }

  return <form className="form-fields" action={async (form) => submit(form)}>
    <label>Work email<input type="email" name="email" autoComplete="email" placeholder="you@company.com" required/></label>
    <label>Password<span className="password-input"><input type={showPassword ? "text" : "password"} name="password" autoComplete="current-password" placeholder="Enter your password" required/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword(!showPassword)}>{showPassword ? <EyeOff size={17}/> : <Eye size={17}/>}</button></span></label>
    <div className="form-options"><label className="check-label"><input type="checkbox" name="remember"/> Remember me</label><a href="mailto:support@trustflow360.com?subject=Password%20reset">Forgot password?</a></div>
    {error && <p className="form-error" role="alert">{error}</p>}
    <button className="button form-submit" type="submit" disabled={busy}>{busy ? "Signing in…" : <>Sign in <ArrowRight size={17}/></>}</button>
  </form>;
}
