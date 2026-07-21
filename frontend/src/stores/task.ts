import type { Message } from "@/utils/response";
import { TaskWebSocket } from "@/utils/websocket";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

function genId() {
  return `tmsg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useTaskStore = defineStore("task", () => {
  // 每个 task 的进度/结果消息（system 进度 + agent 最终答案）
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

  function now() {
    return new Date().toISOString();
  }

  function handleProgressEvent(taskId: string, data: Record<string, any>) {
    const event = data?.event;

    // 节点完成：追加一条进度 system 消息 + 更新当前步骤
    if (event === "node_end") {
      const stage = data.data?.stage ?? "";
      const title = data.data?.title ?? stage;
      const desc = data.data?.desc ?? "";
      appendMessage(taskId, {
        id: data.id ?? genId(),
        msg_type: "system",
        type: "info",
        content: `[${stage}] ${title}${desc ? "：" + desc : ""}`,
        created_at: now(),
      } as Message);
      currentStep.value = stage || currentStep.value;
      return;
    }

    // 任务结束：停止运行态，展示最终答案（agent 气泡，走 Markdown/LaTeX 渲染）
    if (event === "task_end") {
      isRunning.value = false;
      completed.value = true;
      currentStep.value = "已完成";
      if (data.data?.final_response) {
        appendMessage(taskId, {
          id: "final-" + taskId,
          msg_type: "agent",
          content: data.data.final_response,
          created_at: now(),
        });
      } else if (data.data?.message) {
        appendMessage(taskId, {
          id: genId(),
          msg_type: "system",
          type: "error",
          content: "任务失败：" + data.data.message,
          created_at: now(),
        } as Message);
      }
      return;
    }
  }

  function connectWebSocket(taskId: string) {
    if (ws) { ws.close(); ws = null; }
    setCurrentTask(taskId);
    ensureTaskBucket(taskId);
    isRunning.value = true;
    completed.value = false;
    currentStep.value = "";

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
    messages, wsStatus, isRunning, completed, currentStep, currentTaskId,
    connectWebSocket, closeWebSocket, setCurrentTask, appendMessage,
  };
});
