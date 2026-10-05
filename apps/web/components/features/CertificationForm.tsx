"use client";

import { useState } from "react";
import { Plus } from "lucide-react";

export function CertificationForm({ vendorId }: { vendorId: string }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  async function create(form: FormData) {
    setMessage(""); setError("");
    try {
      const response = await fetch(`/api/backend/vendors/${vendorId}/certifications`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(form.entries())) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Could not add certificate.");
      setMessage("Certification added. Refresh this passport to see it."); setOpen(false);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not add certificate."); }
  }
  return <div className="cert-form-wrap"><button className="small-link" onClick={()=>setOpen(!open)}><Plus size={14}/> Add certification</button>{message&&<p className="feature-success">{message}</p>}{open&&<form action={create} className="cert-form"><label>Certificate name<input name="name" required placeholder="ISO 27001"/></label><label>Issuer<input name="issuer"/></label><label>Certificate number<input name="certificate_number"/></label><label>Expiry<input name="expires_on" type="date"/></label>{error&&<p className="feature-error" role="alert">{error}</p>}<button className="button">Save certificate</button></form>}</div>;
}
