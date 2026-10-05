"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Logo } from "@/components/Logo";

type Step = "account" | "organization" | "workspace" | "complete";
const steps: Step[] = ["account", "organization", "workspace"];
const labels = ["Your account", "Organization", "Workspace"];

export function SignupWizard() {
  const router = useRouter();
  const params = useSearchParams();
  const [step, setStep] = useState<Step>(params.get("step") === "organization" ? "organization" : "account");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [account, setAccount] = useState({ firstName: "", lastName: "", email: "", password: "" });
  const [organization, setOrganization] = useState({ name: "", website: "", industry: "", size: "", country: "" });
  const [workspace, setWorkspace] = useState({ name: "", slug: "" });
  const currentStep = steps.indexOf(step);

  function updateOrganization(field: keyof typeof organization, value: string) {
    setOrganization((current) => ({ ...current, [field]: value }));
    if (field === "name" && !workspace.slug) setWorkspace((current) => ({ ...current, name: value, slug: value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") }));
  }

  async function submitAccount(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    const data = new FormData(event.currentTarget);
    const nextAccount = { firstName: String(data.get("firstName")), lastName: String(data.get("lastName")), email: String(data.get("email")), password: String(data.get("password")) };
    if (nextAccount.password !== data.get("confirmPassword")) { setError("Passwords do not match."); setBusy(false); return; }
    try {
      const response = await fetch("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ first_name: nextAccount.firstName, last_name: nextAccount.lastName, email: nextAccount.email, password: nextAccount.password }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Could not create your account.");
      setAccount(nextAccount); setStep("organization");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The service is unavailable. Try again shortly."); }
    finally { setBusy(false); }
  }

  async function submitOrganization(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      const response = await fetch("/api/organizations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: organization.name, website: organization.website || null, industry: organization.industry || null, size: organization.size || null, country: organization.country || null, workspace_name: workspace.name || organization.name, slug: workspace.slug }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Could not create your organization.");
      setStep("complete");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The service is unavailable. Try again shortly."); }
    finally { setBusy(false); }
  }

  function continueOrganization(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setStep("workspace");
  }

  return <main className="signup-layout"><header className="signup-header"><Link href="/"><Logo/></Link><span>Already have an account? <Link href="/login">Sign in</Link></span></header>
    {step !== "complete" ? <section className="signup-content"><div className="signup-progress">{labels.map((label, index)=><span className={index <= currentStep ? "step-active" : ""} key={label}><i>{index < currentStep ? <Check size={12}/> : index + 1}</i>{label}</span>).flatMap((item,index)=>index < 2 ? [item,<b key={`line-${index}`}/>] : [item])}</div>
      <div className="signup-card"><div className="eyebrow">{currentStep === 0 ? "GET STARTED IN A FEW MINUTES" : currentStep === 1 ? "TELL US ABOUT YOUR COMPANY" : "MAKE THIS WORKSPACE YOURS"}</div>
        {step === "account" && <><h1>Build trust from day one.</h1><p>Create your admin account to get started.</p><form className="form-fields signup-fields" onSubmit={submitAccount}><div className="name-fields"><label>First name<input name="firstName" autoComplete="given-name" required placeholder="Sofia"/></label><label>Last name<input name="lastName" autoComplete="family-name" required placeholder="Khan"/></label></div><label>Business email<input name="email" type="email" autoComplete="email" required placeholder="you@company.com"/></label><label>Create password<input name="password" type="password" autoComplete="new-password" minLength={10} required placeholder="At least 10 characters"/></label><label>Confirm password<input name="confirmPassword" type="password" autoComplete="new-password" minLength={10} required placeholder="Enter your password again"/></label><label className="check-label terms-check"><input type="checkbox" required/> I agree to the <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button form-submit" disabled={busy}>{busy ? "Creating account…" : <>Continue <ArrowRight size={17}/></>}</button></form></>}
        {step === "organization" && <><h1>Set up your organization.</h1><p>Tell us a little about your company.</p><form className="form-fields signup-fields" onSubmit={continueOrganization}><label>Company name<input value={organization.name} onChange={(event)=>updateOrganization("name",event.target.value)} required placeholder="NexaTel Communications"/></label><div className="name-fields"><label>Industry<select value={organization.industry} onChange={(event)=>updateOrganization("industry",event.target.value)} required><option value="">Select industry</option>{["Technology","Telecommunications","Manufacturing","Financial services","Healthcare","Logistics","Professional services","Other"].map(item=><option key={item}>{item}</option>)}</select></label><label>Company size<select value={organization.size} onChange={(event)=>updateOrganization("size",event.target.value)} required><option value="">Select size</option>{["1-50","51-200","201-1,000","1,001-5,000","5,000+"].map(item=><option key={item}>{item}</option>)}</select></label></div><div className="name-fields"><label>Company website<input type="url" value={organization.website} onChange={(event)=>updateOrganization("website",event.target.value)} placeholder="https://company.com"/></label><label>Country<input value={organization.country} onChange={(event)=>updateOrganization("country",event.target.value)} required placeholder="Pakistan"/></label></div>{error && <p className="form-error" role="alert">{error}</p>}<div className="wizard-actions"><button type="button" className="button button-quiet" onClick={()=>setStep("account")}><ArrowLeft size={16}/> Back</button><button className="button">Continue <ArrowRight size={17}/></button></div></form></>}
        {step === "workspace" && <><h1>Name your workspace.</h1><p>Choose the name and unique URL your team will use.</p><form className="form-fields signup-fields" onSubmit={submitOrganization}><label>Workspace name<input value={workspace.name} onChange={(event)=>setWorkspace({...workspace,name:event.target.value})} required placeholder="NexaTel"/></label><label>Workspace URL<span className="slug-input"><i>trustflow360.com/</i><input value={workspace.slug} onChange={(event)=>setWorkspace({...workspace,slug:event.target.value.toLowerCase().replace(/[^a-z0-9-]/g,"")})} required pattern="[a-z0-9]+(?:-[a-z0-9]+)*"/></span></label><p className="workspace-note">Your account: {account.email}</p>{error && <p className="form-error" role="alert">{error}</p>}<div className="wizard-actions"><button type="button" className="button button-quiet" onClick={()=>setStep("organization")}><ArrowLeft size={16}/> Back</button><button className="button" disabled={busy}>{busy ? "Creating workspace…" : <>Create workspace <ArrowRight size={17}/></>}</button></div></form></>}
      </div><Link href="/" className="signup-back"><ArrowLeft size={15}/> Return to TrustFlow</Link></section> : <section className="signup-content signup-complete"><div className="complete-check"><Check size={27}/></div><div className="eyebrow">YOU’RE READY</div><h1>Welcome to TrustFlow 360.</h1><p>{workspace.name || organization.name} workspace is set up for your team. Invite teammates and start mapping trusted relationships.</p><div className="complete-details"><span><Check size={15}/> Admin account created</span><span><Check size={15}/> Organization configured</span><span><Check size={15}/> Workspace URL reserved</span></div><button className="button" onClick={()=>router.push("/dashboard")}>Open your dashboard <ArrowRight size={17}/></button></section>}
    <footer className="signup-footer">© 2026 TrustFlow 360 <span>Secure enterprise onboarding</span></footer></main>;
}
