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
        :is-running="chatSession.isRunning"
        empty-text="开始建模"
        empty-subtext="描述你的问题，我将输出完整建模方案和论文"
        input-placeholder="描述你想解决的建模问题..."
        @send="handleUserSend"
      />
    </div>
    <Transition name="slide-right">
      <div v-if="rightPanelOpen" class="w-80 shrink-0 border-l bg-background flex flex-col overflow-y-auto">
        <div>
          <div class="border-b border-border px-4 py-2 flex items-center justify-between cursor-pointer hover:bg-accent/50" @click="progressOpen = !progressOpen">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 执行进度</span>
            <ChevronDown class="h-3 w-3 text-muted-foreground transition-transform" :class="{ 'rotate-180': progressOpen }" />
          </div>
          <div v-if="progressOpen" class="p-4">
            <UserStepper :steps="agentSteps" />
            <p v-if="taskStore.wsStatus !== 'connected' && chatSession.isRunning" class="mt-3 font-mono text-[10px] text-muted-foreground">
              WS 状态: {{ taskStore.wsStatus }}
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { PanelRight, ChevronDown } from "lucide-vue-next";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import { useTaskStore } from "@/stores/task";
import { createTask } from "@/apis/commonApi";
import type { Message } from "@/utils/response";

const chatSession = useChatSessionStore();
const taskStore = useTaskStore();

const rightPanelOpen = ref(true);
const progressOpen = ref(true);

// 当前 solution 会话关联的后端 task_id（本地映射，不持久化后端任务）
const currentTaskId = ref<string | null>(null);

// 步骤定义（与后端 node_meta 对齐）
const stepDefs = [
  { key: "问题分析", label: "问题分析", description: "识别问题类型,理解题意" },
  { key: "模型构建", label: "模型构建", description: "选择并建立数学模型" },
  { key: "求解计算", label: "求解计算", description: "生成并执行求解代码" },
  { key: "验证分析", label: "验证分析", description: "检验模型鲁棒性" },
  { key: "论文写作", label: "论文写作", description: "生成结构化论文" },
];

const agentSteps = computed(() => {
  const current = taskStore.currentStep;
  // 后端 stage 可能是「问题分析/知识检索/计划制定/模型构建/求解计算/验证分析/论文写作/整合输出」
  // 映射到 5 个主步骤：找到第一个 >= current 的主步骤作为 active
  const order = stepDefs.map((s) => s.key);
  let activeIdx = order.indexOf(current);
  if (current === "已完成") {
    return stepDefs.map((s, i) => ({ id: String(i + 1), label: s.label, description: s.description, status: "done" as const }));
  }
  // 若 current 不在主步骤里（如「知识检索」「计划制定」），按最接近的归类
  if (activeIdx === -1) {
    if (current.includes("分析") || current.includes("检索") || current.includes("计划")) activeIdx = 0;
    else if (current.includes("模型")) activeIdx = 1;
    else if (current.includes("求解") || current.includes("计算")) activeIdx = 2;
    else if (current.includes("验证")) activeIdx = 3;
    else if (current.includes("写作") || current.includes("整合") || current.includes("输出")) activeIdx = 4;
  }
  return stepDefs.map((s, i) => ({
    id: String(i + 1),
    label: s.label,
    description: s.description,
    status:
      activeIdx === -1
        ? ("wait" as const)
        : i < activeIdx
        ? ("done" as const)
        : i === activeIdx
        ? ("active" as const)
        : ("wait" as const),
  }));
});

// 聊天面板 = 用户在 solution 会话发的消息 + 该 task 的进度/最终答案
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

  chatSession.isRunning = true;

  try {
    const res = await createTask({ problem: text, mode: "execute" });
    const taskId = res.data?.task_id ?? res.data?.data?.task_id;
    if (!taskId) throw new Error("未返回 task_id");
    currentTaskId.value = taskId;
    // 连接 WS 实时接收进度与最终答案；isRunning 由 task_end 事件驱动
    taskStore.connectWebSocket(taskId);
  } catch (e: any) {
    chatSession.addMessage("solution", sessionId, {
      id: generateId(),
      msg_type: "system",
      type: "error",
      content: `⚠️ 创建任务失败：${e?.message ?? "后端不可达，请确认已启动 (uvicorn app.main:app --port 8000)"}`,
      created_at: new Date().toISOString(),
    } as Message);
    chatSession.isRunning = false;
  }
}

// task_end 后 taskStore.isRunning 置 false，同步到本地运行态
watch(
  () => taskStore.isRunning,
  (running) => {
    chatSession.isRunning = running;
  },
);

onMounted(() => {
  // 刷新/重新进入时恢复最近的 solution 会话，避免空白
  if (!chatSession.activeSolutionId && chatSession.sortedSolutionSessions.length > 0) {
    chatSession.switchSession("solution", chatSession.sortedSolutionSessions[0].id);
  }
});

onUnmounted(() => {
  taskStore.closeWebSocket();
});
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
