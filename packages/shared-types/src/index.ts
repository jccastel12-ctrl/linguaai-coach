/**
 * Shared TypeScript contracts mirroring the API schemas (apps/api/app/domains/<domain>/schemas.py).
 * Keep in sync manually for now; see docs/decisions/ADR-001 for the plan to generate them from OpenAPI.
 */

export type UUID = string;
export type ISODateTime = string;

export const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;
export type CefrLevel = (typeof CEFR_LEVELS)[number];

export const LANGUAGE_CODES = ["es", "en", "sr"] as const;
export type LanguageCode = (typeof LANGUAGE_CODES)[number];

export type ProgressStatus = "not_started" | "in_progress" | "completed";

export interface HealthResponse {
  status: "ok";
  service: string;
  version: string;
  environment: "development" | "test" | "staging" | "production";
}

export interface Language {
  code: string;
  name: string;
  native_name: string;
  is_active: boolean;
}

export interface StudentProfile {
  display_name: string | null;
  native_language_code: string | null;
  timezone: string;
  daily_goal_minutes: number;
  bio: string | null;
}

export interface UserLanguage {
  language_code: string;
  cefr_level: CefrLevel;
  is_primary: boolean;
}

export interface User {
  id: UUID;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  email_verified_at: ISODateTime | null;
  created_at: ISODateTime;
  profile: StudentProfile | null;
  languages: UserLanguage[];
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

export interface LessonSummary {
  id: UUID;
  language_code: string;
  slug: string;
  title: string;
  description: string | null;
  cefr_level: CefrLevel;
  order_index: number;
  estimated_minutes: number;
}

export interface Lesson extends LessonSummary {
  content: Record<string, unknown>;
}

export interface LessonProgress {
  lesson_id: UUID;
  status: ProgressStatus;
  score: number | null;
  completed_at: ISODateTime | null;
}

export interface ApiError {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
}


export type TutorPersonality = "friendly" | "patient" | "professional";
export type TutorTurnRole = "user" | "assistant";
export type LearningMemoryCategory = "grammar" | "vocabulary" | "pronunciation" | "usage";

export interface TutorSession {
  id: UUID;
  target_language_code: string;
  cefr_level: CefrLevel;
  personality: TutorPersonality;
  title: string | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface TutorTurn {
  id: UUID;
  role: TutorTurnRole;
  content: string;
  corrected_text: string | null;
  explanation: string | null;
  translation: string | null;
  created_at: ISODateTime;
}

export interface TutorExchange {
  session_id: UUID;
  user_turn: TutorTurn;
  assistant_turn: TutorTurn;
}

export interface LearningMemory {
  id: UUID;
  language_code: string;
  category: LearningMemoryCategory;
  memory_key: string;
  note: string;
  occurrence_count: number;
  last_example: string | null;
  updated_at: ISODateTime;
}


export interface TutorSessionDetail extends TutorSession {
  turns: TutorTurn[];
}

export interface TutorStats {
  total_sessions: number;
  total_user_messages: number;
  total_corrections: number;
  memory_patterns: number;
  repeated_patterns: number;
  sessions_last_7_days: number;
  most_frequent_category: LearningMemoryCategory | null;
  most_frequent_pattern: string | null;
}

export interface TranslationRequest {
  text: string;
  source_language: LanguageCode;
  target_language: LanguageCode;
}

export interface TranslationResponse {
  source_language: LanguageCode;
  target_language: LanguageCode;
  source_text: string;
  translated_text: string;
  provider: "rule_based" | "openai_compatible";
  learning_note: string | null;
  exact_match: boolean;
}

export interface PronunciationExercise {
  id: string;
  language_code: LanguageCode;
  cefr_level: CefrLevel;
  text: string;
  focus_sound: string | null;
  tip: string;
}

export interface PronunciationEvaluateRequest {
  language_code: LanguageCode;
  cefr_level: CefrLevel;
  expected_text: string;
  recognized_text: string;
  browser_confidence?: number | null;
  focus_sound?: string | null;
}

export interface PronunciationEvaluation {
  id: UUID;
  language_code: LanguageCode;
  cefr_level: CefrLevel;
  expected_text: string;
  recognized_text: string;
  overall_score: number;
  word_accuracy: number;
  transcript_similarity: number;
  browser_confidence: number | null;
  feedback: string;
  focus_sound: string | null;
  missing_words: string[];
  extra_words: string[];
  created_at: ISODateTime;
}

export interface PronunciationStats {
  total_attempts: number;
  average_score: number | null;
  best_score: number | null;
  attempts_last_7_days: number;
}

export type PlanTier = "basic" | "pro";
export type SubscriptionStatus = "active" | "canceled" | "past_due";
export type MeteredFeature = "tutor_message" | "translation" | "pronunciation";

export interface PlanLimits {
  tutor_messages_per_day: number;
  translations_per_day: number;
  pronunciation_attempts_per_day: number;
}

export interface PlanInfo {
  id: PlanTier;
  name: string;
  tagline: string;
  audience: string;
  limits: PlanLimits;
  benefits: string[];
  payment_enabled: boolean;
}

export interface FeatureUsage {
  feature: MeteredFeature;
  label: string;
  used: number;
  limit: number;
  remaining: number;
}

export interface BillingOverview {
  plan: PlanInfo;
  status: SubscriptionStatus;
  requested_plan: PlanTier | null;
  usage: FeatureUsage[];
  resets_at: ISODateTime;
  payment_enabled: boolean;
}

export interface UpgradeRequestResponse {
  requested_plan: PlanTier;
  message: string;
}


export interface PaymentCapabilities {
  provider: string;
  checkout_enabled: boolean;
  webhooks_enabled: boolean;
  note: string;
}

export interface AdminUsageSummary {
  tutor_message: number;
  translation: number;
  pronunciation: number;
}

export interface AdminOverview {
  total_users: number;
  active_users: number;
  pro_users: number;
  pending_upgrade_requests: number;
  new_users_last_7_days: number;
  usage_today: AdminUsageSummary;
  payment_provider: string;
  checkout_enabled: boolean;
}

export interface AdminUser {
  id: UUID;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  email_verified_at: ISODateTime | null;
  created_at: ISODateTime;
  plan_tier: PlanTier;
  subscription_status: SubscriptionStatus;
  requested_plan: PlanTier | null;
  payment_provider: string | null;
}

export interface AdminUserList {
  items: AdminUser[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminAuditEvent {
  id: UUID;
  actor_user_id: UUID | null;
  target_user_id: UUID;
  action: string;
  old_plan: string | null;
  new_plan: string | null;
  note: string | null;
  created_at: ISODateTime;
}
