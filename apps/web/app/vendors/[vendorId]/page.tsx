import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, BadgeCheck, Building2, CircleAlert, FileCheck2, ShieldCheck } from "lucide-react";
import { FeatureShell } from "@/components/features/FeatureShell";
import { CertificationForm } from "@/components/features/CertificationForm";
import { CertificationRow } from "@/components/features/CertificationRow";
import { serverApi } from "@/lib/server-api";

type Passport = {
  vendor: { id: string; vendor_number: string; name: string; category: string; country: string; verification_status: string; risk_level: string; status: string; trust_score: number; compliance_score: number; delivery_score: number; active_contracts: number; registration_number?: string | null; tax_id?: string | null };
  certifications: { id: string; name: string; issuer?: string; certificate_number?: string; expires_on?: string; verified: boolean }[];
  verified_certifications: number;
  blockchain_proof: string;
};

export default async function VendorPassportPage({ params }: { params: Promise<{ vendorId: string }> }) {
  const { vendorId } = await params;
  const passport = await serverApi<Passport>(`/vendors/${vendorId}/passport`);
  if (!passport) notFound();
  const { vendor } = passport;
  return <FeatureShell><section className="passport-page"><Link className="passport-back" href="/vendors"><ArrowLeft size={15}/> All vendors</Link><div className="passport-heading"><div><span className="passport-mark"><Building2 size={24}/></span><div><div className="eyebrow">TRUST PASSPORT · {vendor.vendor_number}</div><h1>{vendor.name}</h1><p>{vendor.category} · {vendor.country}</p></div></div><span className={`feature-status status-${vendor.verification_status}`}>{vendor.verification_status}</span></div><div className="passport-grid"><article className="passport-score"><span>TRUST SCORE</span><strong>{Math.round(vendor.trust_score)}<small>/100</small></strong><div className="score-track"><i style={{width:`${vendor.trust_score}%`}}/></div><p>Calculated from identity, compliance, delivery and current verification status.</p></article><article className="passport-card"><span><ShieldCheck size={18}/> Identity & registration</span><b>{vendor.registration_number || "Registration not provided"}</b><small>Tax record: {vendor.tax_id || "Pending"}</small></article><article className="passport-card"><span><BadgeCheck size={18}/> Delivery performance</span><b>{Math.round(vendor.delivery_score)} / 100</b><small>{vendor.active_contracts} active contracts</small></article><article className="passport-card"><span><CircleAlert size={18}/> Risk & compliance</span><b>{vendor.risk_level} risk · {Math.round(vendor.compliance_score)} compliance</b><small>Relationship status: {vendor.status}</small></article></div><section className="panel passport-certificates"><div className="panel-heading"><div><h2><FileCheck2 size={16}/> Certifications</h2><p>{passport.verified_certifications} verified of {passport.certifications.length} records</p></div><CertificationForm vendorId={vendor.id}/></div>{passport.certifications.length?passport.certifications.map((item)=><CertificationRow key={item.id} vendorId={vendor.id} item={item}/>):<p className="feature-empty">No certificates are recorded yet.</p>}</section><p className="passport-proof"><ShieldCheck size={16}/> Proof status: {passport.blockchain_proof.replaceAll("_"," ")}. Create a local SHA-256 proof from the Proof Ledger for workspace verification.</p></section></FeatureShell>;
}
