import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Logo } from "@/components/Logo";
import { ThemePicker } from "@/components/ThemePicker";

const links = [["Vendors", "/vendors"], ["RFQs", "/rfqs"], ["Bids", "/bids"], ["Approvals", "/approvals"], ["Contracts", "/contracts"], ["Purchase orders", "/purchase-orders"], ["Shipments", "/shipments"], ["Finance", "/finance"], ["Risk & compliance", "/risks"], ["Credentials", "/credentials"], ["Assets", "/assets"], ["Proof ledger", "/proofs"], ["Trust assistant", "/assistant"], ["People & access", "/organization"]];

export function FeatureShell({ children }: { children: React.ReactNode }) {
  return <main className="feature-layout"><header className="feature-topbar"><Link href="/dashboard"><Logo/></Link><nav>{links.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav><ThemePicker/><Link href="/dashboard" className="feature-back"><ArrowLeft size={15}/> Dashboard</Link></header><div className="feature-content">{children}</div></main>;
}
