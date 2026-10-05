import { NextResponse } from "next/server";
import type { LoginRequest, TokenResponse } from "@/types";
import { backendFetch, readApiError, setSessionToken } from "@/lib/server-auth";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as LoginRequest | null;
  if (!body?.email || !body?.password) {
    return NextResponse.json({ detail: "Correo y contraseña son obligatorios." }, { status: 400 });
  }

  try {
    const response = await backendFetch("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
    }

    const token = (await response.json()) as TokenResponse;
    await setSessionToken(token.access_token, token.expires_in);

    const me = await backendFetch("/api/v1/auth/me", {}, token.access_token);
    if (!me.ok) {
      return NextResponse.json({ detail: "La sesión se creó, pero no fue posible validar el usuario." }, { status: 502 });
    }

    return NextResponse.json(await me.json());
  } catch {
    return NextResponse.json({ detail: "No fue posible conectar con el servicio de autenticación." }, { status: 503 });
  }
}
