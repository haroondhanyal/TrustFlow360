import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";
export default async function ShipmentsPage() { const rows = await serverApi<Record<string, unknown>[]>("/operations/shipments"); if (!rows) redirect("/login"); return <FeatureShell><FeatureWorkspace module="shipments" initialRows={rows}/></FeatureShell>; }
