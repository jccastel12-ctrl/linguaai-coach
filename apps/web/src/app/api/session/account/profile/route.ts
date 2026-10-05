import { NextResponse } from "next/server";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

export async function PATCH(request: Request) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  if (!body) return NextResponse.json({ detail: "Datos inválidos." }, { status: 400 });

  const userResponse = await backendFetch(
    "/api/v1/users/me",
    { method: "PATCH", body: JSON.stringify({ full_name: body.full_name ?? null }) },
    token,
  );
  if (!userResponse.ok) return NextResponse.json({ detail: await readApiError(userResponse) }, { status: userResponse.status });

  const profileResponse = await backendFetch(
    "/api/v1/users/me/profile",
    {
      method: "PATCH",
      body: JSON.stringify({
        display_name: body.display_name ?? null,
        native_language_code: body.native_language_code ?? null,
        daily_goal_minutes: body.daily_goal_minutes,
        bio: body.bio ?? null,
      }),
    },
    token,
  );
  if (!profileResponse.ok) return NextResponse.json({ detail: await readApiError(profileResponse) }, { status: profileResponse.status });

  return NextResponse.json({ user: await userResponse.json(), profile: await profileResponse.json() });
}
