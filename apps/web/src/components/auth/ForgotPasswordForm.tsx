"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
export function ForgotPasswordForm() {
  const [email,setEmail]=useState(""); const [message,setMessage]=useState(""); const [loading,setLoading]=useState(false);
  async function submit(e:FormEvent){e.preventDefault();setLoading(true);const r=await fetch("/api/account/password-reset/request",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email})});const p=await r.json().catch(()=>null);setMessage(p?.message ?? "Si la cuenta existe, recibirás instrucciones.");setLoading(false);}
  return <form className="auth-form" onSubmit={submit}><div className="field-group"><label htmlFor="email">Correo electrónico</label><input id="email" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)} /></div>{message?<p className="form-success">{message}</p>:null}<button className="button button-primary button-block" disabled={loading}>{loading?"Enviando…":"Enviar enlace"}</button><p className="auth-switch"><Link href="/login">Volver al inicio de sesión</Link></p></form>;
}
