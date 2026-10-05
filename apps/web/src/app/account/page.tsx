import { redirect } from "next/navigation";
import { AccountSettings } from "@/components/account/AccountSettings";
import { getCurrentUser } from "@/lib/server-auth";

export default async function AccountPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  return <section className="account-shell"><div><span className="eyebrow">Cuenta</span><h1 className="page-title">Perfil y seguridad</h1><p className="muted">Actualiza tus datos y protege el acceso a LinguaAI Coach.</p></div><AccountSettings user={user} /></section>;
}
