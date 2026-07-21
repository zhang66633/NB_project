/** 流式对话组合式函数 — /chat 与 /teach 页共用。
 *
 * 负责：会话创建/复用、用户消息与 agent 占位消息写入、
 * 调 SSE 接口并流式就地累加、运行态管理、最新会话恢复。
 */
import { useChatSessionStore, type SessionMode } from "@/stores/chatSession";
import { streamChat, type ChatHistoryMessage } from "@/apis/chatApi";
import type { Message } from "@/utils/response";

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function useStreamChat(sessionMode: SessionMode, chatMode: "chat" | "teach") {
  const chatSession = useChatSessionStore();

  /** 当前会话消息 → 后端历史格式（仅 user/assistant，跳过流式中的空消息）。 */
  function buildHistory(): ChatHistoryMessage[] {
    return chatSession
      .getActiveMessages(sessionMode)
      .value.filter((m) => (m.msg_type === "user" || m.msg_type === "agent") && m.content)
      .map((m) => ({
        role: m.msg_type === "user" ? "user" : "assistant",
        content: m.content as string,
      }));
  }

  async function handleUserSend(text: string) {
    let sessionId = chatSession.getActiveId(sessionMode).value;
    if (!sessionId) {
      sessionId = chatSession.createSession(sessionMode);
    }

    const userMsg: Message = {
      id: generateId(),
      msg_type: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    chatSession.addMessage(sessionMode, sessionId, userMsg);

    // 占位一条 agent 空消息，后续流式就地累加（streaming 标记跳过打字机重放）
    const agentMsg: Message = {
      id: generateId(),
      msg_type: "agent",
      content: "",
      streaming: true,
      created_at: new Date().toISOString(),
    };
    chatSession.addMessage(sessionMode, sessionId, agentMsg);

    chatSession.isRunning = true;

    let acc = "";
    await streamChat(buildHistory(), {
      mode: chatMode,
      onDelta(delta) {
        acc += delta;
        chatSession.updateMessage(sessionMode, sessionId, agentMsg.id, { content: acc });
      },
      onDone() {
        chatSession.updateMessage(sessionMode, sessionId, agentMsg.id, {
          content: acc || "（未收到回复内容）",
          streaming: false,
        });
        chatSession.isRunning = false;
      },
      onError(message) {
        chatSession.updateMessage(sessionMode, sessionId, agentMsg.id, {
          content: `出错了：${message}`,
          streaming: false,
        });
        chatSession.isRunning = false;
      },
    });
  }

  /** 无激活会话时，切到最近一条会话（供 onMounted 调用）。 */
  function restoreLatestSession() {
    const active = chatSession.getActiveId(sessionMode).value;
    const sorted = chatSession.getSortedSessions(sessionMode).value;
    if (!active && sorted.length > 0) {
      chatSession.switchSession(sessionMode, sorted[0].id);
    }
  }

  return { handleUserSend, restoreLatestSession };
}
