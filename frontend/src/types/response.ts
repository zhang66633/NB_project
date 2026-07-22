/** 对应后端消息结构定义 */
import type { AgentType } from "./enum";

/** 系统消息类型 */
export type SystemMessageType = "info" | "warning" | "success" | "error";

/** 消息基础接口 */
export interface BaseMessage {
  id: string;
  created_at?: string;
  msg_type: "system" | "agent" | "user" | "tool";
  content?: string | null;
  /** 流式增量更新中（此时跳过打字机效果，直接全量渲染） */
  streaming?: boolean;
}

/** 工具调用消息 */
export interface ToolMessage extends BaseMessage {
  msg_type: "tool";
  tool_name: string;
  input: Record<string, unknown> | null;
  output: unknown[] | null;
}

/** 系统通知消息 */
export interface SystemMessage extends BaseMessage {
  msg_type: "system";
  type: SystemMessageType;
}

/** 用户消息 */
export interface UserMessage extends BaseMessage {
  msg_type: "user";
}

/** Agent 消息基类 */
export interface AgentMessage extends BaseMessage {
  msg_type: "agent";
  /** 流水线 agent 类型；纯对话（chat/teach）消息无此字段 */
  agent_type?: AgentType;
}

/** 所有消息类型的联合类型 */
export type Message =
  | SystemMessage
  | UserMessage
  | AgentMessage
  | ToolMessage;
