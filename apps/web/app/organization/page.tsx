import { redirect } from "next/navigation";
import { FeatureShell } from "@/components/features/FeatureShell";
import { OrganizationWorkspace } from "@/components/features/OrganizationWorkspace";
import { serverApi } from "@/lib/server-api";

export default async function OrganizationPage() {
  const [departments, members, roles, invitations] = await Promise.all([
    serverApi<{id:string;name:string;description?:string}[]>("/organization/departments"),
    serverApi<{id:string;email:string;first_name:string;last_name:string;role:string;department_id:string|null;is_active:boolean}[]>("/organization/users"),
    serverApi<{roles:{key:string;name:string;permissions:string[]}[];custom_roles:{key:string;name:string;permissions:string[]}[]}>("/organization/roles"),
    serverApi<{id:string;email:string;role:string;department_id?:string|null;expires_at:string;accepted:boolean}[]>("/organization/invitations"),
  ]);
  if (!departments || !members || !roles || !invitations) redirect("/login");
  return <FeatureShell><OrganizationWorkspace initialDepartments={departments} initialMembers={members} initialRoles={roles} initialInvitations={invitations}/></FeatureShell>;
}
