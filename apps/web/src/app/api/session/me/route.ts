import { NextResponse } from "next/server";
import { backendFetch, clearSessionToken, getSessionToken, readApiError } from "@/lib/server-auth";

export async function GET() {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  try {
    const response = await backendFetch("/api/v1/auth/me", {}, token);
    if (!response.ok) {
      if (response.status === 401) await clearSessionToken();
      return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
    }
    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json({ detail: "No fue posible validar la sesión." }, { status: 503 });
  }
}
