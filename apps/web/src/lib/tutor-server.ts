import "server-only";

import type { LearningMemory, TutorSession, TutorSessionDetail, TutorStats } from "@/types";
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

export async function getTutorSessions(limit = 20): Promise<TutorSession[]> {
  return (await authedJson<TutorSession[]>(`/api/v1/tutor/sessions?limit=${limit}`)) ?? [];
}

export async function getTutorSession(sessionId: string): Promise<TutorSessionDetail | null> {
  return authedJson<TutorSessionDetail>(`/api/v1/tutor/sessions/${encodeURIComponent(sessionId)}`);
}

export async function getTutorMemory(limit = 50): Promise<LearningMemory[]> {
  return (await authedJson<LearningMemory[]>(`/api/v1/tutor/memory?limit=${limit}`)) ?? [];
}

export async function getTutorStats(): Promise<TutorStats | null> {
  return authedJson<TutorStats>("/api/v1/tutor/stats");
}
