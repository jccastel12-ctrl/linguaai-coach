import { NextResponse } from "next/server";
import type { CefrLevel, TutorExchange, TutorPersonality, TutorSession } from "@/types";
import { backendFetch, getSessionToken, readApiError } from "@/lib/server-auth";

interface TutorMessageBody {
  session_id?: string | null;
  target_language_code: string;
  cefr_level: CefrLevel;
  personality: TutorPersonality;
  message: string;
}

export async function POST(request: Request) {
  const token = await getSessionToken();
  if (!token) return NextResponse.json({ detail: "No autenticado." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as TutorMessageBody | null;
  if (!body?.message?.trim() || !body.target_language_code || !body.cefr_level || !body.personality) {
    return NextResponse.json({ detail: "Faltan datos para iniciar la conversación." }, { status: 400 });
  }

  try {
    let sessionId = body.session_id ?? null;

    if (!sessionId) {
      const sessionResponse = await backendFetch(
        "/api/v1/tutor/sessions",
        {
          method: "POST",
          body: JSON.stringify({
            target_language_code: body.target_language_code,
            cefr_level: body.cefr_level,
            personality: body.personality,
          }),
        },
        token,
      );

      if (!sessionResponse.ok) {
        return NextResponse.json(
          { detail: await readApiError(sessionResponse) },
          { status: sessionResponse.status },
        );
      }
      const session = (await sessionResponse.json()) as TutorSession;
      sessionId = session.id;
    }

    const messageResponse = await backendFetch(
      `/api/v1/tutor/sessions/${sessionId}/messages`,
      { method: "POST", body: JSON.stringify({ text: body.message.trim() }) },
      token,
    );

    if (!messageResponse.ok) {
      return NextResponse.json(
        { detail: await readApiError(messageResponse) },
        { status: messageResponse.status },
      );
    }

    const exchange = (await messageResponse.json()) as TutorExchange;
    return NextResponse.json(exchange);
  } catch {
    return NextResponse.json({ detail: "No fue posible conectar con el tutor." }, { status: 503 });
  }
}
