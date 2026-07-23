/** 自由问答（纯对话）SSE 流式接口封装。
 *
 * 不走 axios（不便读流），用 fetch + ReadableStream 解析 SSE 分帧。
 */

export interface ChatHistoryMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ToolCallEvent {
  name: string;
  args: Record<string, unknown>;
}

export interface ToolResultEvent {
  name: string;
  preview: string;
}

export interface StreamChatOptions {
  /** 每次收到增量文本时回调 */
  onDelta: (delta: string) => void;
  /** LLM 决定调用某个工具时回调（args 已完整） */
  onToolCall?: (event: ToolCallEvent) => void;
  /** 工具执行完成时回调（含结果预览） */
  onToolResult?: (event: ToolResultEvent) => void;
  /** 流正常结束回调 */
  onDone?: () => void;
  /** 出错回调（网络错误或服务端 error 帧） */
  onError?: (message: string) => void;
  /** 可选：外部中止 */
  signal?: AbortSignal;
  useRag?: boolean;
  /** 对话模式：chat=自由问答（默认），teach=教学模式（引导式） */
  mode?: "chat" | "teach";
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

function getToken(): string | null {
  return (
    localStorage.getItem("mma-token") ||
    localStorage.getItem("token") ||
    localStorage.getItem("access_token")
  );
}

export async function streamChat(
  messages: ChatHistoryMessage[],
  opts: StreamChatOptions,
): Promise<void> {
  const { onDelta, onToolCall, onToolResult, onDone, onError, signal, useRag = false, mode = "chat" } = opts;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ messages, use_rag: useRag, mode }),
      signal,
    });
  } catch (e: any) {
    if (e?.name === "AbortError") return;
    onError?.(`网络错误，无法连接后端：${e?.message ?? e}`);
    return;
  }

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    onError?.(`请求失败 (${response.status})：${text || response.statusText}`);
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    onError?.("浏览器不支持流式读取");
    return;
  }

  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const line = frame.trim();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();

        if (payload === "[DONE]") {
          onDone?.();
          return;
        }

        try {
          const obj = JSON.parse(payload);
          if (obj.error) {
            onError?.(obj.error);
            return;
          }
          if (obj.delta) {
            onDelta(obj.delta);
          }
          if (obj.tool_call) {
            onToolCall?.(obj.tool_call);
          }
          if (obj.tool_result) {
            onToolResult?.(obj.tool_result);
          }
        } catch {
          // 非 JSON 帧，忽略
        }
      }
    }
    onDone?.();
  } catch (e: any) {
    if (e?.name !== "AbortError") {
      onError?.(`流读取中断：${e?.message ?? e}`);
    }
  }
}