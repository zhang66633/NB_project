import { ref, computed } from "vue";
import { defineStore } from "pinia";
import type { Message } from "@/utils/response";

export type SessionMode = "chat" | "teach" | "solution";

export interface ChatSession {
  id: string;
  title: string;
  mode: SessionMode;
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
    const chatSessions = ref<ChatSession[]>([]);
    const teachSessions = ref<ChatSession[]>([]);
    const solutionSessions = ref<ChatSession[]>([]);

    const activeChatId = ref<string | null>(null);
    const activeTeachId = ref<string | null>(null);
    const activeSolutionId = ref<string | null>(null);

    const isRunning = ref(false);

    function getSessions(mode: SessionMode) {
      switch (mode) {
        case "chat": return chatSessions;
        case "teach": return teachSessions;
        case "solution": return solutionSessions;
      }
    }

    function getActiveId(mode: SessionMode) {
      switch (mode) {
        case "chat": return activeChatId;
        case "teach": return activeTeachId;
        case "solution": return activeSolutionId;
      }
    }

    function setActiveId(mode: SessionMode, id: string | null) {
      switch (mode) {
        case "chat": activeChatId.value = id; break;
        case "teach": activeTeachId.value = id; break;
        case "solution": activeSolutionId.value = id; break;
      }
    }

    const sortedChatSessions = computed(() =>
      [...chatSessions.value].sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
    );
    const sortedTeachSessions = computed(() =>
      [...teachSessions.value].sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
    );
    const sortedSolutionSessions = computed(() =>
      [...solutionSessions.value].sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
    );

    function getSortedSessions(mode: SessionMode) {
      switch (mode) {
        case "chat": return sortedChatSessions;
        case "teach": return sortedTeachSessions;
        case "solution": return sortedSolutionSessions;
      }
    }

    const activeChatSession = computed(() =>
      chatSessions.value.find((s) => s.id === activeChatId.value) ?? null,
    );
    const activeTeachSession = computed(() =>
      teachSessions.value.find((s) => s.id === activeTeachId.value) ?? null,
    );
    const activeSolutionSession = computed(() =>
      solutionSessions.value.find((s) => s.id === activeSolutionId.value) ?? null,
    );

    function getActiveSession(mode: SessionMode) {
      switch (mode) {
        case "chat": return activeChatSession;
        case "teach": return activeTeachSession;
        case "solution": return activeSolutionSession;
      }
    }

    const activeChatMessages = computed(() => activeChatSession.value?.messages ?? []);
    const activeTeachMessages = computed(() => activeTeachSession.value?.messages ?? []);
    const activeSolutionMessages = computed(() => activeSolutionSession.value?.messages ?? []);

    function getActiveMessages(mode: SessionMode) {
      switch (mode) {
        case "chat": return activeChatMessages;
        case "teach": return activeTeachMessages;
        case "solution": return activeSolutionMessages;
      }
    }

    function createSession(mode: SessionMode): string {
      const id = genId();
      const titleMap: Record<SessionMode, string> = {
        chat: "新对话",
        teach: "新学习",
        solution: "新方案",
      };
      const session: ChatSession = {
        id,
        title: titleMap[mode],
        mode,
        messages: [],
        createdAt: now(),
        updatedAt: now(),
      };
      getSessions(mode).value.push(session);
      setActiveId(mode, id);
      return id;
    }

    function switchSession(mode: SessionMode, id: string) {
      const list = getSessions(mode).value;
      if (list.some((s) => s.id === id)) {
        setActiveId(mode, id);
      }
    }

    function deleteSession(mode: SessionMode, id: string) {
      const list = getSessions(mode).value;
      const idx = list.findIndex((s) => s.id === id);
      if (idx === -1) return;
      list.splice(idx, 1);
      const activeId = getActiveId(mode);
      if (activeId.value === id) {
        const sorted = getSortedSessions(mode).value;
        setActiveId(mode, sorted[0]?.id ?? null);
      }
    }

    function renameSession(mode: SessionMode, id: string, newTitle: string) {
      const list = getSessions(mode).value;
      const session = list.find((s) => s.id === id);
      if (!session) return;
      session.title = newTitle.trim() || "新对话";
      session.updatedAt = now();
    }

    function addMessage(mode: SessionMode, sessionId: string, msg: Message) {
      const list = getSessions(mode).value;
      const session = list.find((s) => s.id === sessionId);
      if (!session) return;
      session.messages.push(msg);
      session.updatedAt = now();
      const defaultTitle: Record<SessionMode, string> = {
        chat: "新对话",
        teach: "新学习",
        solution: "新方案",
      };
      if (session.title === defaultTitle[mode] && msg.msg_type === "user" && msg.content) {
        session.title = msg.content.slice(0, 30) + (msg.content.length > 30 ? "..." : "");
      }
    }

    function addMessageToActive(mode: SessionMode, msg: Message) {
      const activeId = getActiveId(mode).value;
      if (!activeId) return;
      addMessage(mode, activeId, msg);
    }

    function clearActive(mode: SessionMode) {
      setActiveId(mode, null);
    }

    return {
      chatSessions, teachSessions, solutionSessions,
      activeChatId, activeTeachId, activeSolutionId,
      isRunning,
      sortedChatSessions, sortedTeachSessions, sortedSolutionSessions,
      activeChatSession, activeTeachSession, activeSolutionSession,
      activeChatMessages, activeTeachMessages, activeSolutionMessages,
      createSession, switchSession, deleteSession, renameSession,
      addMessage, addMessageToActive, clearActive,
      getSessions, getActiveId, getSortedSessions, getActiveSession, getActiveMessages,
    };
  },
  {
    persist: {
      key: "mma-chat-sessions",
      storage: localStorage,
      pick: ["chatSessions", "teachSessions", "solutionSessions", "activeChatId", "activeTeachId", "activeSolutionId"],
    },
  },
);
