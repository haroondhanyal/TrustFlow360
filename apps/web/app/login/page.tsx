import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Logo } from "@/components/Logo";
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return <main className="auth-layout"><section className="auth-brand-panel"><Link href="/"><Logo/></Link><div className="auth-message"><div className="eyebrow"><span className="pulse"/> TRUST, BUILT INTO EVERY STEP</div><h1>Make confidence<br/>your <em>default.</em></h1><p>See the full picture behind every partner, purchase and promise.</p><div className="auth-quote"><div className="quote-bars"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div><strong>94<span>/100</span></strong><small>PORTFOLIO TRUST SCORE</small></div></div><div className="auth-panel-foot">AI-assisted insight <i/> Verifiable by design <i/> Enterprise ready</div></section>
    <section className="auth-form-side"><Link href="/" className="back-link"><ArrowLeft size={16}/> Back to home</Link><div className="auth-form-wrap"><span className="form-kicker">YOUR WORKSPACE AWAITS</span><h2>Welcome back</h2><p className="form-intro">Sign in to continue to your TrustFlow workspace.</p><LoginForm/><p className="form-bottom">New to TrustFlow? <Link href="/signup">Create an account</Link></p></div><div className="legal-links"><a href="mailto:privacy@trustflow360.com">Privacy contact</a><a href="mailto:legal@trustflow360.com">Terms contact</a><span>© 2026 TrustFlow 360</span></div></section></main>
}
