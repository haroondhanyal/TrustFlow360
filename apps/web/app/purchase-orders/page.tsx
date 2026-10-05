import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function PurchaseOrdersPage() {
  const [orders, vendors, contracts] = await Promise.all([
    serverApi<Record<string, unknown>[]>("/purchase-orders"),
    serverApi<Record<string, unknown>[]>("/vendors?status=active"),
    serverApi<Record<string, unknown>[]>("/contracts"),
  ]);
  if (!orders || !vendors || !contracts) redirect("/login");
  return <FeatureShell><FeatureWorkspace module="purchase-orders" initialRows={orders} choices={{vendors: vendors.filter((vendor) => vendor.verification_status === "verified"),contracts: contracts.filter((contract) => contract.status === "active")}}/></FeatureShell>;
}
