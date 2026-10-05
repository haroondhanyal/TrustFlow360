import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { TrustAssistant } from "@/components/features/OperationsTools";
import { serverApi } from "@/lib/server-api";
export default async function AssistantPage() { const rows = await serverApi<Record<string, unknown>[]>("/operations/shipments"); if (!rows) redirect("/login"); return <FeatureShell><TrustAssistant/></FeatureShell>; }
