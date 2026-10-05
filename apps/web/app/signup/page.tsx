import { Suspense } from "react";
import { SignupWizard } from "@/components/auth/SignupWizard";

export default function SignupPage() {
  return <Suspense fallback={<main className="signup-layout"><p className="loading-message">Loading secure onboarding…</p></main>}><SignupWizard/></Suspense>;
}
