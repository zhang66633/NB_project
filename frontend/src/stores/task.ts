import type { Message } from "@/utils/response";
import { TaskWebSocket } from "@/utils/websocket";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useTaskStore = defineStore("task", () => {
  const messagesByTask = ref<Record<string, Message[]>>({});
  const currentTaskId = ref<string | null>(null);
  let ws: TaskWebSocket | null = null;
  const wsStatus = ref<"connecting" | "connected" | "disconnected" | "reconnecting">("disconnected");
  const isRunning = ref(false);

  const messages = computed<Message[]>(() => {
    if (!currentTaskId.value) return [];
    return messagesByTask.value[currentTaskId.value] ?? [];
  });

  function ensureTaskBucket(taskId: string) {
    if (!messagesByTask.value[taskId]) {
      messagesByTask.value[taskId] = [];
    }
  }

  function appendMessage(taskId: string, message: Message) {
    ensureTaskBucket(taskId);
    messagesByTask.value[taskId] = [...messagesByTask.value[taskId], message];
  }

  function setCurrentTask(taskId: string) {
    currentTaskId.value = taskId;
  }

  function connectWebSocket(taskId: string) {
    if (ws) { ws.close(); ws = null; }
    setCurrentTask(taskId);
    ensureTaskBucket(taskId);
    isRunning.value = true;

    const baseUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
    const wsUrl = `${baseUrl}/task/${taskId}`;

    ws = new TaskWebSocket(
      wsUrl,
      (data) => {
        if (data && typeof data === "object" && "id" in (data as Record<string, unknown>)) {
          appendMessage(taskId, data as Message);
        }
      },
      (status) => { wsStatus.value = status; },
    );
    ws.connect();
  }

  function closeWebSocket() {
    ws?.close();
    ws = null;
  }

  return {
    messages, wsStatus, isRunning,
    connectWebSocket, closeWebSocket,
    setCurrentTask, appendMessage,
  };
});
