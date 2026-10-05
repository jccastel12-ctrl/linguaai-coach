"use client";

import { FormEvent, useState } from "react";
import type { User } from "@/types";

const languageNames: Record<string, string> = { es: "Español", en: "English", sr: "Srpski" };

export function AccountSettings({ user }: { user: User }) {
  const [fullName, setFullName] = useState(user.full_name ?? "");
  const [displayName, setDisplayName] = useState(user.profile?.display_name ?? "");
  const [nativeLanguage, setNativeLanguage] = useState(user.profile?.native_language_code ?? "es");
  const [dailyGoal, setDailyGoal] = useState(user.profile?.daily_goal_minutes ?? 15);
  const [bio, setBio] = useState(user.profile?.bio ?? "");
  const [profileMessage, setProfileMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [saving, setSaving] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [verificationMessage, setVerificationMessage] = useState("");

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProfileError(""); setProfileMessage(""); setSaving(true);
    try {
      const response = await fetch("/api/session/account/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName.trim() || null,
          display_name: displayName.trim() || null,
          native_language_code: nativeLanguage,
          daily_goal_minutes: dailyGoal,
          bio: bio.trim() || null,
        }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) { setProfileError(payload?.detail ?? "No fue posible guardar los cambios."); return; }
      setProfileMessage("Perfil actualizado.");
    } catch { setProfileError("No fue posible conectar con el servidor."); }
    finally { setSaving(false); }
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordError(""); setPasswordMessage("");
    if (newPassword.length < 10) { setPasswordError("La nueva contraseña debe tener al menos 10 caracteres."); return; }
    if (newPassword !== confirmPassword) { setPasswordError("Las contraseñas no coinciden."); return; }
    const response = await fetch("/api/session/account/password", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) { setPasswordError(payload?.detail ?? "No fue posible cambiar la contraseña."); return; }
    setCurrentPassword(""); setNewPassword(""); setConfirmPassword("");
    setPasswordMessage("Contraseña actualizada. Por seguridad, vuelve a iniciar sesión.");
    window.setTimeout(() => { window.location.href = "/login"; }, 1200);
  }

  async function resendVerification() {
    setVerificationMessage("");
    const response = await fetch("/api/session/account/verification", { method: "POST" });
    const payload = await response.json().catch(() => null);
    setVerificationMessage(response.ok ? (payload?.message ?? "Solicitud enviada.") : (payload?.detail ?? "No fue posible enviar el enlace."));
  }

  return (
    <div className="account-grid">
      <section className="card account-card">
        <div><span className="eyebrow">Perfil</span><h2>Tu información</h2></div>
        <form className="auth-form" onSubmit={saveProfile}>
          <div className="field-group"><label>Nombre completo</label><input value={fullName} onChange={(e) => setFullName(e.target.value)} maxLength={120} /></div>
          <div className="field-group"><label>Nombre visible</label><input value={displayName} onChange={(e) => setDisplayName(e.target.value)} maxLength={80} /></div>
          <div className="field-group"><label>Idioma nativo</label><select value={nativeLanguage} onChange={(e) => setNativeLanguage(e.target.value)}>{Object.entries(languageNames).map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select></div>
          <div className="field-group"><label>Meta diaria (minutos)</label><input type="number" min={1} max={480} value={dailyGoal} onChange={(e) => setDailyGoal(Number(e.target.value))} /></div>
          <div className="field-group"><label>Acerca de ti</label><textarea value={bio} onChange={(e) => setBio(e.target.value)} maxLength={1000} rows={4} /></div>
          {profileError ? <p className="form-error">{profileError}</p> : null}
          {profileMessage ? <p className="form-success">{profileMessage}</p> : null}
          <button className="button button-primary" disabled={saving}>{saving ? "Guardando…" : "Guardar cambios"}</button>
        </form>
      </section>

      <div className="account-side-stack">
        <section className="card account-card">
          <span className="eyebrow">Correo</span><h2>Verificación</h2>
          <p><strong>{user.email}</strong></p>
          <p className={user.email_verified_at ? "status-good" : "status-warning"}>{user.email_verified_at ? "✓ Correo verificado" : "Correo pendiente de verificación"}</p>
          {!user.email_verified_at ? <button className="button button-secondary" type="button" onClick={resendVerification}>Reenviar enlace</button> : null}
          {verificationMessage ? <p className="muted">{verificationMessage}</p> : null}
        </section>

        <section className="card account-card">
          <span className="eyebrow">Seguridad</span><h2>Cambiar contraseña</h2>
          <form className="auth-form" onSubmit={changePassword}>
            <div className="field-group"><label>Contraseña actual</label><input type="password" autoComplete="current-password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required /></div>
            <div className="field-group"><label>Nueva contraseña</label><input type="password" autoComplete="new-password" minLength={10} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required /></div>
            <div className="field-group"><label>Confirmar nueva contraseña</label><input type="password" autoComplete="new-password" minLength={10} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required /></div>
            {passwordError ? <p className="form-error">{passwordError}</p> : null}
            {passwordMessage ? <p className="form-success">{passwordMessage}</p> : null}
            <button className="button button-secondary">Actualizar contraseña</button>
          </form>
        </section>
      </div>
    </div>
  );
}
