/** Agent 类型枚举 — 扩展了源项目，增加了 2 个 Agent */
export enum AgentType {
  ORCHESTRATOR = "OrchestratorAgent",
  ANALYSIS = "AnalysisAgent",
  MODELING = "ModelingAgent",
  SOLVING = "SolvingAgent",
  VERIFICATION = "VerificationAgent",
  WRITING = "WritingAgent",
}

/** LLM API 类型枚举 */
export enum ApiType {
  OPENAI_CHAT = "openai-chat",
  OPENAI_RESPONSES = "openai-responses",
  ANTHROPIC = "anthropic",
}

/** 任务模式 */
export enum TaskMode {
  TEACH = "teach",
  EXECUTE = "execute",
}
