import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Logo } from "@/components/Logo";

const links = [["Vendors", "/vendors"], ["RFQs", "/rfqs"], ["Bids", "/bids"], ["Approvals", "/approvals"], ["Contracts", "/contracts"], ["Purchase orders", "/purchase-orders"], ["People & access", "/organization"]];

export function FeatureShell({ children }: { children: React.ReactNode }) {
  return <main className="feature-layout"><header className="feature-topbar"><Link href="/dashboard"><Logo/></Link><nav>{links.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav><Link href="/dashboard" className="feature-back"><ArrowLeft size={15}/> Dashboard</Link></header><div className="feature-content">{children}</div></main>;
}
