import { Suspense } from "react";
import Link from "next/link";
import { Logo } from "@/components/Logo";
import { JoinForm } from "@/components/auth/JoinForm";

export default function JoinPage() {
  return <main className="auth-layout"><section className="auth-brand-panel"><Link href="/"><Logo/></Link><div className="auth-message"><div className="eyebrow">A TRUSTED TEAM INVITED YOU</div><h1>Work better,<br/><em>together.</em></h1><p>Join your organization’s verified workspace and collaborate with your team.</p></div><div className="auth-panel-foot">Secure invitation <i/> Expires after seven days</div></section><section className="auth-form-side"><div className="auth-form-wrap"><span className="form-kicker">TEAM INVITATION</span><h2>Join your workspace</h2><p className="form-intro">Create your member account to accept this invitation.</p><Suspense fallback={<p className="loading-message">Loading invitation…</p>}><JoinForm/></Suspense></div></section></main>;
}
