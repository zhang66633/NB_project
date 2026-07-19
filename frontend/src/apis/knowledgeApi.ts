/** Knowledge base API — search, browse, and manage the KB. */
import request from "@/utils/request";

// ── types ──────────────────────────────────────────────────────────

export interface SearchResult {
  id: string;
  type: "method_card" | "paper" | "template";
  name: string;
  title: string;
  snippet: string;
  score: number | null;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}

export interface KBStats {
  methods_count: number;
  papers_count: number;
  templates_count: number;
  total: number;
}

export interface MethodCardSummary {
  id: string;
  name: string;
  category: string[];
  applicable_when: string[];
  typical_scenarios: string[];
}

export interface MethodCardDetail extends MethodCardSummary {
  principle: string;
  formulas: { name: string; latex: string; description: string }[];
  not_applicable_when: string[];
  common_mistakes: { mistake: string; solution: string }[];
  code_snippets: { language: string; description: string; code: string }[];
  related_cards: string[];
  related_papers: string[];
}

export interface PaperSummary {
  id: string;
  year: number;
  competition: string;
  problem_id: string;
  title: string;
  tags: Record<string, string[]>;
  quality_rating: number;
}

export interface PaperDetail extends PaperSummary {
  analysis: Record<string, unknown>;
  model: Record<string, unknown>;
  evaluation: Record<string, unknown>;
  source: string;
}

export interface TemplateSummary {
  id: string;
  name: string;
  applicable_to: string[];
  steps_count: number;
}

export interface TemplateDetail {
  id: string;
  name: string;
  applicable_to: string[];
  steps: { step: number; name: string; guiding_questions: string[]; decision_tree: string[]; checklist: string[] }[];
}

// ── API functions ──────────────────────────────────────────────────

/** Search the knowledge base. */
export function searchKB(params: {
  q: string;
  type?: string;
  problem_type?: string;
  k?: number;
}) {
  return request.get<SearchResponse>("/knowledge/search", { params });
}

/** Get knowledge base statistics. */
export function getKBStats() {
  return request.get<KBStats>("/knowledge/stats");
}

/** Trigger a full reindex. */
export function reindexKB() {
  return request.post<{ success: boolean; indexed_count: number; message: string }>("/knowledge/reindex");
}

/** List method cards. */
export function listMethods(category?: string) {
  return request.get<MethodCardSummary[]>("/knowledge/methods", {
    params: category ? { category } : {},
  });
}

/** Get a single method card by ID. */
export function getMethod(cardId: string) {
  return request.get<MethodCardDetail>(`/knowledge/methods/${cardId}`);
}

/** List papers. */
export function listPapers(params?: {
  problem_type?: string;
  competition?: string;
  year?: number;
}) {
  return request.get<PaperSummary[]>("/knowledge/papers", { params });
}

/** Get a single paper by ID. */
export function getPaper(paperId: string) {
  return request.get<PaperDetail>(`/knowledge/papers/${paperId}`);
}

/** List templates. */
export function listTemplates(problemType?: string) {
  return request.get<TemplateSummary[]>("/knowledge/templates", {
    params: problemType ? { problem_type: problemType } : {},
  });
}

/** Get a single template by ID. */
export function getTemplate(tplId: string) {
  return request.get<TemplateDetail>(`/knowledge/templates/${tplId}`);
}

// ── CRUD operations ──────────────────────────────────────────────

export interface CrudResponse {
  success: boolean;
  entry_id: string;
  message: string;
}

export interface JobStatus {
  job_id: string;
  status: "processing" | "completed" | "error";
  result?: {
    entry_id: string;
    entry_type: string;
    file_path: string;
    yaml_content: string;
  };
  error?: string;
}

/** Upload raw text or file for LLM extraction. */
export function uploadKnowledge(params: {
  text?: string;
  file?: File;
  kb_type: string;
  name?: string;
}) {
  const formData = new FormData();
  if (params.text) formData.append("text", params.text);
  if (params.file) formData.append("file", params.file);
  formData.append("kb_type", params.kb_type);
  if (params.name) formData.append("name", params.name);
  return request.post<{ job_id: string; status: string }>(
    "/knowledge/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
}

/** Poll extraction job status. */
export function getExtractionJob(jobId: string) {
  return request.get<JobStatus>(`/knowledge/jobs/${jobId}`);
}

/** Create method card. */
export function createMethod(data: Record<string, unknown>) {
  return request.post<CrudResponse>("/knowledge/methods", data);
}

/** Update method card. */
export function updateMethod(cardId: string, data: Record<string, unknown>) {
  return request.put<CrudResponse>(`/knowledge/methods/${cardId}`, data);
}

/** Delete method card. */
export function deleteMethod(cardId: string) {
  return request.delete<CrudResponse>(`/knowledge/methods/${cardId}`);
}

/** Create paper. */
export function createPaper(data: Record<string, unknown>) {
  return request.post<CrudResponse>("/knowledge/papers", data);
}

/** Update paper. */
export function updatePaper(paperId: string, data: Record<string, unknown>) {
  return request.put<CrudResponse>(`/knowledge/papers/${paperId}`, data);
}

/** Delete paper. */
export function deletePaper(paperId: string) {
  return request.delete<CrudResponse>(`/knowledge/papers/${paperId}`);
}

/** Create template. */
export function createTemplate(data: Record<string, unknown>) {
  return request.post<CrudResponse>("/knowledge/templates", data);
}

/** Update template. */
export function updateTemplate(tplId: string, data: Record<string, unknown>) {
  return request.put<CrudResponse>(`/knowledge/templates/${tplId}`, data);
}

/** Delete template. */
export function deleteTemplate(tplId: string) {
  return request.delete<CrudResponse>(`/knowledge/templates/${tplId}`);
}
