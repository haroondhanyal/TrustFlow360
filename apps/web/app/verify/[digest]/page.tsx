import Link from "next/link";
import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { serverApi } from "@/lib/server-api";
export default async function VerifyProofPage({ params }: {params: Promise<{digest:string}>}) {
  const {digest}=await params;
  const result=await serverApi<{valid:boolean;digest:string;statement:Record<string,unknown>;scope:string}>(`/operations/verify/${encodeURIComponent(digest)}`);
  if (!result) redirect("/login");
  return <FeatureShell><section className="feature-workspace"><div className="eyebrow">PROOF VERIFICATION</div><h1>{result.valid?"Proof verified":"Proof check failed"}</h1><p>This verification checks the record hash against the current workspace ledger.</p><p className={result.valid?"feature-message feature-success":"feature-message feature-error"}>{result.valid?"Digest matches the recorded statement.":"Digest does not match the recorded statement."}</p><dl><dt>SHA-256</dt><dd><code>{result.digest}</code></dd><dt>Record</dt><dd>{String(result.statement.name??result.statement.id??"Workspace record")}</dd><dt>Scope</dt><dd>{result.scope}</dd></dl><Link className="button" href="/proofs">Back to proof ledger</Link></section></FeatureShell>;
}
