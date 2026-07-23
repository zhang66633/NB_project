<template>
  <div class="flex h-full bg-background">
    <div class="flex-1 min-w-0 relative">
      <button
        class="absolute top-2 right-2 z-10 inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-background/80 backdrop-blur hover:bg-accent transition-colors"
        title="切换执行进度面板"
        @click="rightPanelOpen = !rightPanelOpen"
      >
        <PanelRight class="h-4 w-4" />
      </button>
      <ChatArea
        :messages="displayMessages"
        :is-running="chatSession.getIsRunning('solution').value"
        :cancellable="!!currentTaskId"
        :cancelling="cancelling"
        empty-text="开始建模"
        empty-subtext="描述你的问题，我将输出完整建模方案和论文"
        input-placeholder="描述你想解决的建模问题..."
        @send="handleUserSend"
        @cancel="handleCancel"
      >
        <template #progress>
          <ProgressTimeline
            v-if="rightPanelOpen === false || true"
            class="mx-4 sm:mx-8 mt-2 mb-4"
            :steps="agentSteps"
            :running="taskStore.isRunning"
            :completed="taskStore.completed"
            :ws-status="taskStore.wsStatus"
            :open="true"
            @toggle="rightPanelOpen = !rightPanelOpen"
          />
        </template>
      </ChatArea>
    </div>
    <Transition name="slide-right">
      <div v-if="rightPanelOpen" class="w-80 shrink-0 border-l bg-background p-4 overflow-y-auto">
        <ProgressTimeline
          :steps="agentSteps"
          :running="taskStore.isRunning"
          :completed="taskStore.completed"
          :ws-status="taskStore.wsStatus"
          :open="true"
          @toggle="rightPanelOpen = !rightPanelOpen"
        />
        <div v-if="currentTaskId" class="mt-3 font-mono text-[10px] text-muted-foreground break-all">
          Task ID: {{ currentTaskId }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { PanelRight } from "lucide-vue-next";
import ChatArea from "@/components/ChatArea.vue";
import ProgressTimeline, { type ProgressStep } from "@/components/ProgressTimeline.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import { useTaskStore } from "@/stores/task";
import { createTask, cancelTask } from "@/apis/commonApi";
import type { Message } from "@/types/response";

const chatSession = useChatSessionStore();
const taskStore = useTaskStore();

const rightPanelOpen = ref(true);

// 关联的 task_id 放到 taskStore（持久化），避免切页后丢失导致进度/结果不渲染。
// 见 stores/task.ts 的 solutionTaskId 字段。
const currentTaskId = computed({
  get: () => taskStore.solutionTaskId,
  set: (v: string | null) => { taskStore.solutionTaskId = v; },
});
const cancelling = ref(false);

const stepDefs: ProgressStep[] = [
  { id: "1", label: "问题分析", description: "识别问题类型，理解题意", status: "wait" },
  { id: "2", label: "模型构建", description: "选择并建立数学模型", status: "wait" },
  { id: "3", label: "求解计算", description: "生成并执行求解代码", status: "wait" },
  { id: "4", label: "验证分析", description: "检验模型鲁棒性", status: "wait" },
  { id: "5", label: "论文写作", description: "生成结构化论文", status: "wait" },
];

const agentSteps = computed<ProgressStep[]>(() => {
  const current = taskStore.currentStep;
  if (taskStore.completed) {
    return stepDefs.map((s) => ({ ...s, status: "done" }));
  }
  if (!current) {
    return stepDefs;
  }
  const order = stepDefs.map((s) => s.label);
  let activeIdx = order.indexOf(current);
  if (current === "已完成") {
    return stepDefs.map((s) => ({ ...s, status: "done" }));
  }
  if (activeIdx === -1) {
    if (current.includes("分析") || current.includes("检索") || current.includes("计划")) activeIdx = 0;
    else if (current.includes("模型")) activeIdx = 1;
    else if (current.includes("求解") || current.includes("计算")) activeIdx = 2;
    else if (current.includes("验证")) activeIdx = 3;
    else if (current.includes("写作") || current.includes("整合") || current.includes("输出")) activeIdx = 4;
  }
  return stepDefs.map((s, i) => ({
    ...s,
    status:
      activeIdx === -1
        ? "wait"
        : i < activeIdx
          ? "done"
          : i === activeIdx
            ? "active"
            : "wait",
  }));
});

const displayMessages = computed<Message[]>(() => {
  const userMsgs = chatSession.activeSolutionMessages;
  const taskMsgs = currentTaskId.value ? taskStore.messages : [];
  return [...userMsgs, ...taskMsgs];
});

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

async function handleUserSend(text: string) {
  let sessionId = chatSession.activeSolutionId;
  if (!sessionId) {
    sessionId = chatSession.createSession("solution");
  }

  const userMsg: Message = {
    id: generateId(),
    msg_type: "user",
    content: text,
    created_at: new Date().toISOString(),
  };
  chatSession.addMessage("solution", sessionId, userMsg);

  // 如果已有任务在跑，先拒绝发送
  if (chatSession.runningMode !== null) {
    chatSession.addMessage("solution", sessionId, {
      id: generateId(),
      msg_type: "system",
      type: "error",
      content: "⚠️ 当前已有任务在执行，请先等待或停止。",
      created_at: new Date().toISOString(),
    } as Message);
    return;
  }

  chatSession.setRunning("solution");

  try {
    const res = await createTask({ problem: text, mode: "execute" });
    const taskId = res.data?.task_id ?? res.data?.data?.task_id;
    if (!taskId) throw new Error("未返回 task_id");
    currentTaskId.value = taskId;
    // 连接 WS 实时接收进度与最终答案；task_end 事件会清空 runningMode
    taskStore.connectWebSocket(taskId);
  } catch (e: any) {
    chatSession.addMessage("solution", sessionId, {
      id: generateId(),
      msg_type: "system",
      type: "error",
      content: `⚠️ 创建任务失败：${e?.message ?? "后端不可达，请确认已启动 (uvicorn app.main:app --port 8000)"}`,
      created_at: new Date().toISOString(),
    } as Message);
    chatSession.setRunning(null);
    currentTaskId.value = null;
  }
}

async function handleCancel() {
  if (!currentTaskId.value || cancelling.value) return;
  cancelling.value = true;
  try {
    await cancelTask(currentTaskId.value);
    // 后端会主动推 task_end/canceled 事件，前端通过 WS 收尾
  } catch (e: any) {
    console.error("取消任务失败：", e);
  } finally {
    // 兜底：若 WS 没收到 cancel 事件，2s 后强制清状态
    setTimeout(() => {
      cancelling.value = false;
      if (chatSession.runningMode === "solution") {
        chatSession.setRunning(null);
      }
    }, 2000);
  }
}

// task_end 后 taskStore.isRunning=false，同步 solution 的 runningMode
watch(
  () => taskStore.isRunning,
  (running) => {
    if (!running && chatSession.runningMode === "solution") {
      chatSession.setRunning(null);
    }
  },
);

onMounted(() => {
  if (!chatSession.activeSolutionId && chatSession.sortedSolutionSessions.length > 0) {
    chatSession.switchSession("solution", chatSession.sortedSolutionSessions[0].id);
  }
  // 切回 solution 页时：connectWebSocket 内部有短路逻辑
  // - 已连到目标 task → 直接复用
  // - 断开 / 连接到别的 task → 重连
  // 这样切页回来不会卡"思考中"，也不会重复打开 WS 把进度搞丢。
  if (taskStore.solutionTaskId && !taskStore.completed) {
    taskStore.connectWebSocket(taskStore.solutionTaskId);
  }
});

// 注意：故意不在 onUnmounted 关闭 WS / 清空 task_id，避免切页导致任务进度丢失。
// WS 与 solutionTaskId 都由 taskStore 持有，task_end 事件会清运行态。
onBeforeUnmount(() => {});
</script>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.25s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>