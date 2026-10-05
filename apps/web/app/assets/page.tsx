import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";
export default async function AssetsPage() { const rows = await serverApi<Record<string, unknown>[]>("/operations/assets"); if (!rows) redirect("/login"); return <FeatureShell><FeatureWorkspace module="assets" initialRows={rows}/></FeatureShell>; }
