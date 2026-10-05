import { NextResponse } from "next/server";
import type { TranslationRequest, TranslationResponse } from "@/types";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

export async function POST(request: Request) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as TranslationRequest | null;
  if (!body?.text?.trim() || !body.source_language || !body.target_language) {
    return NextResponse.json({ detail: "Completa el texto y los idiomas." }, { status: 400 });
  }
  if (body.source_language === body.target_language) {
    return NextResponse.json({ detail: "Elige dos idiomas diferentes." }, { status: 400 });
  }

  try {
    const response = await backendFetch(
      "/api/v1/translate",
      {
        method: "POST",
        body: JSON.stringify({
          text: body.text.trim(),
          source_language: body.source_language,
          target_language: body.target_language,
        }),
      },
      token,
    );

    if (!response.ok) {
      return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
    }

    return NextResponse.json((await response.json()) as TranslationResponse);
  } catch {
    return NextResponse.json({ detail: "No fue posible conectar con el traductor." }, { status: 503 });
  }
}
