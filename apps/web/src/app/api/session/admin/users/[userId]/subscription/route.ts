import { NextResponse } from "next/server";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

export async function PATCH(request: Request, context: { params: Promise<{ userId: string }> }) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado" }, { status: 401 });
  const { userId } = await context.params;
  const body = await request.text();
  const response = await backendFetch(`/api/v1/admin/users/${userId}/subscription`, { method: "PATCH", body }, token);
  if (!response.ok) return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
  return NextResponse.json(await response.json());
}
