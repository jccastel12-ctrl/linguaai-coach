import { NextResponse } from "next/server";
import type { RegisterRequest, TokenResponse } from "@/types";
import { backendFetch, readApiError, setSessionToken } from "@/lib/server-auth";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as RegisterRequest | null;
  if (!body?.email || !body?.password) {
    return NextResponse.json({ detail: "Correo y contraseña son obligatorios." }, { status: 400 });
  }

  try {
    const register = await backendFetch("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    });

    if (!register.ok) {
      return NextResponse.json({ detail: await readApiError(register) }, { status: register.status });
    }

    const login = await backendFetch("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: body.email, password: body.password }),
    });

    if (!login.ok) {
      return NextResponse.json({ detail: await readApiError(login) }, { status: login.status });
    }

    const token = (await login.json()) as TokenResponse;
    await setSessionToken(token.access_token, token.expires_in);

    return NextResponse.json(await register.json(), { status: 201 });
  } catch {
    return NextResponse.json({ detail: "No fue posible conectar con el servicio de registro." }, { status: 503 });
  }
}
