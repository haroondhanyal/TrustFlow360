"use client";

import { useState } from "react";
import { BadgeCheck, FileCheck2 } from "lucide-react";

type Certification = { id:string; name:string; issuer?:string; certificate_number?:string; verified:boolean };

export function CertificationRow({ vendorId, item }: { vendorId:string; item:Certification }) {
  const [verified,setVerified] = useState(item.verified);
  const [error,setError] = useState("");
  async function verify() {
    setError("");
    const response=await fetch(`/api/backend/vendors/${vendorId}/certifications/${item.id}/verify`,{method:"POST"});
    if(response.ok) setVerified(true);
    else { const result=await response.json(); setError(result.detail??"Could not verify this certificate."); }
  }
  return <article className="certificate-row"><span className="certificate-icon"><FileCheck2 size={17}/></span><span><b>{item.name}</b><small>{item.issuer||"Issuer not recorded"} · {item.certificate_number||"No certificate number"}</small>{error&&<small className="feature-error">{error}</small>}</span>{verified?<span className="feature-status status-verified"><BadgeCheck size={12}/> verified</span>:<button className="small-link" onClick={verify}>Verify</button>}</article>;
}
