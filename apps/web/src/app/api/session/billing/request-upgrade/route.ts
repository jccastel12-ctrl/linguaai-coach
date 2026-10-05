import { NextResponse } from "next/server";
import type { UpgradeRequestResponse } from "@/types";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

export async function POST() {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  try {
    const response = await backendFetch(
      "/api/v1/billing/me/request-upgrade",
      { method: "POST" },
      token,
    );
    if (!response.ok) {
      return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
    }
    return NextResponse.json((await response.json()) as UpgradeRequestResponse);
  } catch {
    return NextResponse.json({ detail: "No fue posible registrar la solicitud." }, { status: 503 });
  }
}
