import { NextResponse } from "next/server";
import type { PronunciationEvaluateRequest, PronunciationEvaluation } from "@/types";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

export async function POST(request: Request) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as PronunciationEvaluateRequest | null;
  if (!body?.expected_text?.trim() || !body.recognized_text?.trim() || !body.language_code || !body.cefr_level) {
    return NextResponse.json({ detail: "Primero graba la frase para poder evaluarla." }, { status: 400 });
  }

  try {
    const response = await backendFetch(
      "/api/v1/pronunciation/evaluate",
      {
        method: "POST",
        body: JSON.stringify({
          language_code: body.language_code,
          cefr_level: body.cefr_level,
          expected_text: body.expected_text.trim(),
          recognized_text: body.recognized_text.trim(),
          browser_confidence: body.browser_confidence ?? null,
          focus_sound: body.focus_sound ?? null,
        }),
      },
      token,
    );

    if (!response.ok) {
      return NextResponse.json({ detail: await readApiError(response) }, { status: response.status });
    }

    return NextResponse.json((await response.json()) as PronunciationEvaluation);
  } catch {
    return NextResponse.json({ detail: "No fue posible evaluar la práctica." }, { status: 503 });
  }
}
