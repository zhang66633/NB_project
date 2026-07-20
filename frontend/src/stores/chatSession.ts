/** 聊天会话持久化 Store — 多会话管理，对话+任务记录跨页面保留 */
import { ref, computed } from "vue";
import { defineStore } from "pinia";
import type { Message } from "@/utils/response";

export interface ChatSession {
  id: string;
  title: string;
  type: "chat" | "task";
  mode: "teach" | "execute";
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

function now() {
  return new Date().toISOString();
}

function genId() {
  return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useChatSessionStore = defineStore(
  "chatSession",
  () => {
    const sessions = ref<ChatSession[]>([]);
    const activeSessionId = ref<string | null>(null);
    const isRunning = ref(false);

    const activeSession = computed(() =>
      sessions.value.find((s) => s.id === activeSessionId.value) ?? null,
    );

    const activeMessages = computed(() => activeSession.value?.messages ?? []);

    const sortedSessions = computed(() =>
      [...sessions.value].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
      ),
    );

    // ── Chat ─────────────────────────────────────────────

    function createSession(mode: "teach" | "execute" = "execute"): string {
      const id = genId();
      sessions.value.push({
        id,
        title: "新对话",
        type: "chat",
        mode,
        messages: [],
        createdAt: now(),
        updatedAt: now(),
      });
      activeSessionId.value = id;
      return id;
    }

    // ── Task ─────────────────────────────────────────────

    function createTaskSession(taskId: string, title: string, mode: "teach" | "execute"): string {
      // 如果已存在同一 taskId 的会话，直接切换
      const existing = sessions.value.find((s) => s.id === taskId && s.type === "task");
      if (existing) {
        activeSessionId.value = existing.id;
        return existing.id;
      }
      sessions.value.push({
        id: taskId,
        title: title || "新任务",
        type: "task",
        mode,
        messages: [],
        createdAt: now(),
        updatedAt: now(),
      });
      activeSessionId.value = taskId;
      return taskId;
    }

    // ── Common ───────────────────────────────────────────

    function switchSession(id: string) {
      if (sessions.value.some((s) => s.id === id)) {
        activeSessionId.value = id;
      }
    }

    function deleteSession(id: string) {
      const idx = sessions.value.findIndex((s) => s.id === id);
      if (idx === -1) return;
      sessions.value.splice(idx, 1);
      if (activeSessionId.value === id) {
        activeSessionId.value = sortedSessions.value[0]?.id ?? null;
      }
    }

    function addMessage(sessionId: string, msg: Message) {
      const session = sessions.value.find((s) => s.id === sessionId);
      if (!session) return;
      session.messages.push(msg);
      session.updatedAt = now();
      if (session.title === "新对话" && msg.msg_type === "user" && msg.content) {
        session.title = msg.content.slice(0, 30) + (msg.content.length > 30 ? "..." : "");
      }
    }

    function addMessageToActive(msg: Message) {
      if (!activeSessionId.value) return;
      addMessage(activeSessionId.value, msg);
    }

    function clearActive() {
      activeSessionId.value = null;
    }

    return {
      sessions, activeSessionId, isRunning,
      activeSession, activeMessages, sortedSessions,
      createSession, createTaskSession,
      switchSession, deleteSession,
      addMessage, addMessageToActive, clearActive,
    };
  },
  {
    persist: {
      key: "mma-chat-sessions",
      storage: localStorage,
      pick: ["sessions", "activeSessionId"],
    },
  },
);
