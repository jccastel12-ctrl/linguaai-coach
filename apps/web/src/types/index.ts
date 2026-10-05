// Re-export the shared API contracts so app code imports from "@/types".
export * from "@linguaai/shared-types";

// Web-only UI types go below.
export interface NavItem {
  href: string;
  label: string;
}
