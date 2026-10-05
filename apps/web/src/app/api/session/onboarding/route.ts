import { NextResponse } from "next/server";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

interface OnboardingRequest {
  native_language_code: string;
  learning_language_code: string;
  cefr_level: string;
  daily_goal_minutes: number;
}

export async function POST(request: Request) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as OnboardingRequest | null;
  if (!body?.native_language_code || !body?.learning_language_code || !body?.cefr_level) {
    return NextResponse.json({ detail: "Completa la configuración de idioma y nivel." }, { status: 400 });
  }
  if (body.native_language_code === body.learning_language_code) {
    return NextResponse.json({ detail: "El idioma nativo y el idioma de aprendizaje deben ser diferentes." }, { status: 400 });
  }

  try {
    const profile = await backendFetch(
      "/api/v1/users/me/profile",
      {
        method: "PATCH",
        body: JSON.stringify({
          native_language_code: body.native_language_code,
          daily_goal_minutes: body.daily_goal_minutes,
        }),
      },
      token,
    );

    if (!profile.ok) {
      return NextResponse.json({ detail: await readApiError(profile) }, { status: profile.status });
    }

    const language = await backendFetch(
      "/api/v1/users/me/languages",
      {
        method: "PUT",
        body: JSON.stringify({
          language_code: body.learning_language_code,
          cefr_level: body.cefr_level,
          is_primary: true,
        }),
      },
      token,
    );

    if (!language.ok) {
      return NextResponse.json({ detail: await readApiError(language) }, { status: language.status });
    }

    return NextResponse.json({ profile: await profile.json(), language: await language.json() });
  } catch {
    return NextResponse.json({ detail: "No fue posible guardar la configuración inicial." }, { status: 503 });
  }
}
