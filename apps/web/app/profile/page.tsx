import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { FeatureShell } from "@/components/features/FeatureShell";
import { ProfileEditor } from "@/components/profile/ProfileEditor";

export default async function ProfilePage() {
  const cookieStore = await cookies();
  if (!cookieStore.get("tf_access")) redirect("/login?next=/profile");
  return <FeatureShell><ProfileEditor/></FeatureShell>;
}
