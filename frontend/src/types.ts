export interface SourceRef {
  file_name: string;
  page?: number | null;
  excerpt: string;
}

export interface ActivityItem {
  id: string;
  category: string;
  description: string;
  quantity: number;
  unit: string;
  period?: string | null;
  location?: string | null;
  scope_guess?: number | null;
  confidence: number;
  source: SourceRef;
  status: string;
}

export interface EmissionResult {
  item_id: string;
  factor_id: string;
  factor_name: string;
  quantity_in_factor_unit: number;
  factor_value: number;
  factor_unit: string;
  co2e_kg: number;
  scope: number;
  rationale: string;
}

export interface GapItem {
  requirement: string;
  description: string;
  severity: string;
  suggestion: string;
}

export interface ReportSection {
  heading: string;
  content: string;
}

export interface ReportDraft {
  title: string;
  period: string;
  summary: string;
  sections: ReportSection[];
}

export interface AuditEvent {
  ts: string;
  stage: string;
  detail: string;
  duration_ms?: number | null;
}

export interface DocumentT {
  id: string;
  file_name: string;
  mime_type: string;
  size: number;
  text?: string | null;
}

export interface Project {
  id: string;
  name: string;
  created_at: string;
  documents: DocumentT[];
  activities: ActivityItem[];
  emissions: EmissionResult[];
  gaps: GapItem[];
  report: ReportDraft | null;
  audit: AuditEvent[];
}

export interface Totals {
  total_co2e_kg: number;
  by_scope_kg: Record<string, number>;
}

export interface QAResult {
  answer: string;
  citations: string[];
}

export interface Meta {
  mode: "mock" | "gemini";
  models: { extract: string; fast: string };
  factors: { count: number };
}
