import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function RFQsPage() {
  const rfqs = await serverApi<Record<string, unknown>[]>("/rfqs");
  if (!rfqs) redirect("/login");
  return <FeatureShell><FeatureWorkspace module="rfqs" initialRows={rfqs}/></FeatureShell>;
}
