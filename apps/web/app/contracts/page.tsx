import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function ContractsPage() {
  const [contracts, vendors] = await Promise.all([
    serverApi<Record<string, unknown>[]>("/contracts"),
    serverApi<Record<string, unknown>[]>("/vendors?status=active"),
  ]);
  if (!contracts || !vendors) redirect("/login");
  return <FeatureShell><FeatureWorkspace module="contracts" initialRows={contracts} choices={{vendors: vendors.filter((vendor) => vendor.verification_status === "verified")}}/></FeatureShell>;
}
