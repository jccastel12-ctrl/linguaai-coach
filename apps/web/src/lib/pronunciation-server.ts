import "server-only";

import type { CefrLevel, LanguageCode, PronunciationExercise, PronunciationStats } from "@/types";
import { backendFetch, getSessionToken } from "@/lib/server-auth";

async function authedJson<T>(path: string): Promise<T | null> {
  const token = await getSessionToken();
  if (!token) return null;
  try {
    const response = await backendFetch(path, {}, token);
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getPronunciationExercises(
  languageCode: LanguageCode,
  cefrLevel: CefrLevel,
): Promise<PronunciationExercise[]> {
  return (
    (await authedJson<PronunciationExercise[]>(
      `/api/v1/pronunciation/exercises?language_code=${encodeURIComponent(languageCode)}&cefr_level=${encodeURIComponent(cefrLevel)}`,
    )) ?? []
  );
}

export async function getPronunciationStats(): Promise<PronunciationStats | null> {
  return authedJson<PronunciationStats>("/api/v1/pronunciation/stats");
}
