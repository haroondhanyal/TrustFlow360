import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function BidsPage() {
  const [bids, rfqs, vendors] = await Promise.all([
    serverApi<Record<string, unknown>[]>("/bids"),
    serverApi<Record<string, unknown>[]>("/rfqs"),
    serverApi<Record<string, unknown>[]>("/vendors?status=active"),
  ]);
  if (!bids || !rfqs || !vendors) redirect("/login");
  const openRFQs = rfqs.filter((rfq) => rfq.status === "open");
  const verifiedVendors = vendors.filter((vendor) => vendor.verification_status === "verified");
  return <FeatureShell><FeatureWorkspace module="bids" initialRows={bids} choices={{rfqs: openRFQs, vendors: verifiedVendors}}/></FeatureShell>;
}
