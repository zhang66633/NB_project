/** 模型配置 */
export interface ModelConfig {
  apiKey: string;
  baseUrl: string;
  modelId: string;
  apiType: string;
  contextWindow?: number;
}

/** 代码执行结果类型 */
export interface CodeResult {
  stdout?: string;
  stderr?: string;
  error?: string;
  outputs?: Array<{
    type: "text" | "image" | "table" | "latex";
    content: string;
  }>;
}
