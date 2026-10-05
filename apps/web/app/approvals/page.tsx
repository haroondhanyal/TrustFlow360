import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function ApprovalsPage() {
  const approvals = await serverApi<Record<string, unknown>[]>("/approvals");
  if (!approvals) redirect("/login");
  return <FeatureShell><FeatureWorkspace module="approvals" initialRows={approvals}/></FeatureShell>;
}
