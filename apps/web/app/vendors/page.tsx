import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function VendorsPage() {
  const vendors = await serverApi<Record<string, unknown>[]>("/vendors");
  if (!vendors) redirect("/login");
  return <FeatureShell><FeatureWorkspace module="vendors" initialRows={vendors}/></FeatureShell>;
}
