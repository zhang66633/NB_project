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
  const completed = ref(false);
  const currentStep = ref<string>("");

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

  function handleProgressEvent(taskId: string, data: Record<string, any>) {
    const event = data?.event;
    // 节点完成：更新对应进度条目的状态
    if (event === "node_end") {
      const idx = messagesByTask.value[taskId]?.findIndex((m) => m.id === data.id) ?? -1;
      if (idx !== -1) {
        messagesByTask.value[taskId][idx] = {
          ...messagesByTask.value[taskId][idx],
          status: "completed",
          content: `[${data.data?.stage}] ${data.data?.title}：${data.data?.desc}`,
        };
      } else if (data.data?.title) {
        appendMessage(taskId, {
          id: data.id,
          msg_type: "system",
          status: "completed",
          content: `[${data.data?.stage}] ${data.data?.title}：${data.data?.desc}`,
        });
      }
      currentStep.value = data.data?.stage || currentStep.value;
    }
    // 任务结束信号：停止运行态并展示最终答案
    if (event === "task_end") {
      isRunning.value = false;
      completed.value = true;
      currentStep.value = "已完成";
      if (data.data?.final_response) {
        appendMessage(taskId, {
          id: "ai-final-" + taskId,
          msg_type: "ai",
          content: data.data.final_response,
        });
      } else if (data.data?.message) {
        appendMessage(taskId, {
          id: "sys-error-" + taskId,
          msg_type: "system",
          content: "任务失败：" + data.data.message,
        });
      }
      return;
    }
    // 其它事件（含 node_start/progress 等）带 id 的作为消息追加
    if (data && typeof data === "object" && "id" in (data as Record<string, unknown>)) {
      appendMessage(taskId, data as Message);
    }
  }

  function connectWebSocket(taskId: string) {
    if (ws) { ws.close(); ws = null; }
    setCurrentTask(taskId);
    ensureTaskBucket(taskId);
    isRunning.value = true;
    completed.value = false;

    const baseUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/ws";
    const wsUrl = `${baseUrl}/task/${taskId}`;

    ws = new TaskWebSocket(
      wsUrl,
      (data) => handleProgressEvent(taskId, data as Record<string, any>),
      (status) => { wsStatus.value = status; },
    );
    ws.connect();
  }

  function closeWebSocket() {
    ws?.close();
    ws = null;
  }

  return {
    messages, wsStatus, isRunning, completed, currentStep,
    connectWebSocket, closeWebSocket,
    setCurrentTask, appendMessage,
  };
});
