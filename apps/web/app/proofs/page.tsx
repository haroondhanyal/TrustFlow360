import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { ProofLedger } from "@/components/features/OperationsTools";
import { serverApi } from "@/lib/server-api";
export default async function ProofsPage() { const [proofs,...modules] = await Promise.all([serverApi<Record<string,string>[]>("/operations/proofs"), ...["shipments","finance","risks","credentials","assets"].map(kind=>serverApi<Record<string,unknown>[]>(`/operations/${kind}`))]); if (!proofs || modules.some(rows=>!rows)) redirect("/login"); const records=modules.flatMap((rows,index)=>(rows??[]).map(row=>({...row,record_type:["shipments","finance","risks","credentials","assets"][index]}))); return <FeatureShell><ProofLedger records={records} initialProofs={proofs}/></FeatureShell>; }
