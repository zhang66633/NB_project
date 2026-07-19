<template>
  <div class="flex h-screen bg-background">
    <AppSidebar :collapsed="sidebarCollapsed" />

    <div class="flex flex-1 flex-col min-w-0">
      <header class="flex h-14 items-center justify-between border-b px-4 gap-3">
        <div class="flex items-center gap-3">
          <button class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
            @click="sidebarCollapsed = !sidebarCollapsed">
            <PanelLeft class="h-4 w-4" />
          </button>
          <div v-if="hasStarted" class="flex items-center gap-2">
            <h2 class="text-sm font-semibold truncate max-w-[200px]">{{ taskTitle }}</h2>
            <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0"
              :class="currentMode === 'execute' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
              {{ currentMode === 'execute' ? '方案输出' : '教学' }}
            </span>
          </div>
          <span v-else class="text-sm font-semibold">新对话</span>
        </div>
        <div class="flex items-center gap-3">
          <ServiceStatus />
          <button v-if="hasStarted" class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
            @click="rightPanelOpen = !rightPanelOpen">
            <PanelRight class="h-4 w-4" />
          </button>
        </div>
      </header>

      <!-- Welcome -->
      <div v-if="!hasStarted" class="flex-1 flex items-center justify-center">
        <div class="w-full max-w-2xl px-6 text-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mx-auto mb-6">
            <MessageSquare class="h-8 w-8 text-primary" />
          </div>
          <h2 class="text-2xl font-bold mb-2">{{ welcomeMode === 'teach' ? '教学模式' : '方案输出模式' }}</h2>
          <p class="text-muted-foreground mb-8">{{ welcomeMode === 'teach' ? '苏格拉底式引导，逐步培养建模思维' : '结构化输出完整建模方案' }}</p>
          <div class="rounded-2xl border bg-card p-6 shadow-sm">
            <textarea v-model="welcomeProblem" rows="4" placeholder="描述你的数学建模问题..."
              class="w-full resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              @keydown.ctrl.enter="startConversation" />
            <div class="flex items-center justify-between mt-3">
              <div class="flex items-center gap-2">
                <button v-for="mode in modeOptions" :key="mode.value"
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
                  :class="welcomeMode === mode.value ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-accent'"
                  @click="welcomeMode = mode.value">{{ mode.label }}</button>
              </div>
              <button class="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
                @click="startConversation">
                <MessageSquare class="h-4 w-4 mr-1.5" />进入对话
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat -->
      <div v-else class="flex flex-1 min-h-0">
        <div class="flex-1 min-w-0 relative">
          <ChatArea :task-id="currentTaskId" @send="handleUserSend" />
        </div>
        <Transition name="slide-right">
          <div v-if="rightPanelOpen" class="w-80 border-l bg-background flex flex-col overflow-hidden">
            <div class="border-b px-4 py-2 bg-muted/30"><span class="text-xs font-medium text-muted-foreground">执行进度</span></div>
            <div class="flex-1 overflow-y-auto p-4"><UserStepper :steps="agentSteps" /></div>
            <div class="flex-1 border-t overflow-hidden"><NotebookArea :cells="notebookCells" /></div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { PanelLeft, PanelRight, MessageSquare } from "lucide-vue-next";
import AppSidebar from "@/components/AppSidebar.vue";
import ServiceStatus from "@/components/ServiceStatus.vue";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useTaskStore } from "@/stores/task";
import { createTask, getTaskMessages, getTask } from "@/apis/commonApi";
import type { Message } from "@/utils/response";

const route = useRoute();
const taskStore = useTaskStore();

const sidebarCollapsed = ref(false);
const rightPanelOpen = ref(true);
const welcomeProblem = ref("");
const welcomeMode = ref<"teach" | "execute">("teach");
const hasStarted = ref(false);
const currentTaskId = ref("");
const currentMode = ref<"teach" | "execute">("teach");
const taskTitle = ref("新对话");

const modeOptions = [
  { label: "教学模式", value: "teach" as const },
  { label: "方案输出", value: "execute" as const },
];

const agentSteps = ref([
  { id: "1", label: "问题分类", status: "wait" as const, description: "识别问题类型与复杂度" },
  { id: "2", label: "知识检索", status: "wait" as const, description: "从知识库检索方法、论文和模板" },
  { id: "3", label: "问题分析", status: "wait" as const, description: "深度分析问题结构" },
  { id: "4", label: "模型构建", status: "wait" as const, description: "选择或设计数学模型" },
  { id: "5", label: "求解计算", status: "wait" as const, description: "编写代码，执行计算" },
  { id: "6", label: "验证分析", status: "wait" as const, description: "模型验证与鲁棒性分析" },
  { id: "7", label: "论文写作", status: "wait" as const, description: "生成规范论文" },
]);

const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);
let pollTimer: ReturnType<typeof setInterval> | null = null;

// 当后端不可用时的模拟回复
const mockReplies: Record<string, string[]> = {
  teach: [
    "🤔 **让我们一起来分析这个问题。**\n\n首先，你能尝试回答：这个问题的**核心目标**是什么？是最大化某个量，还是最小化？",
    "📝 **很好！下一步我们来看决策变量。**\n\n在这个问题中，哪些因素的值是我们可以决定的？",
    "💡 **现在考虑约束条件。**\n\n我们的决策受到哪些现实条件的限制？试着至少列出 3 条约束。",
  ],
  execute: [
    "📋 **已提交建模任务，智能体正在分析中...**\n\n正在启动多智能体编排流程。后端处理完成后结果将自动显示。",
  ],
};
const replyIndex: Record<string, number> = {};

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function addMsg(msg: Message) {
  if (!currentTaskId.value) return;
  taskStore.appendMessage(currentTaskId.value, msg);
}

function addUserMsg(text: string) {
  addMsg({ id: generateId(), msg_type: "user", content: text, created_at: new Date().toISOString() });
}

async function startConversation() {
  currentMode.value = welcomeMode.value;
  taskTitle.value = welcomeProblem.value.trim() ? welcomeProblem.value.slice(0, 40) + "..." : "新对话";
  const problem = welcomeProblem.value.trim() || "请帮我分析一个数学建模问题";

  // 先进入聊天界面
  const localId = generateId();
  currentTaskId.value = localId;
  hasStarted.value = true;
  taskStore.setCurrentTask(localId);

  addUserMsg(problem);
  taskStore.isRunning = true;

  // 尝试调用后端
  try {
    const res = await createTask({ problem, mode: welcomeMode.value });
    const realTaskId = res.data.task_id;
    // 切换到真实 task ID 并开始轮询
    currentTaskId.value = realTaskId;
    taskStore.setCurrentTask(realTaskId);
    startPolling(realTaskId);
  } catch {
    // 后端不可用 — 用模拟回复
    console.warn("后端不可用，使用模拟回复");
    triggerMockReply(localId);
  }
}

async function handleUserSend(text: string) {
  if (!currentTaskId.value) return;
  addUserMsg(text);
  taskStore.isRunning = true;

  try {
    const res = await createTask({ problem: text, mode: currentMode.value });
    const realTaskId = res.data.task_id;
    currentTaskId.value = realTaskId;
    taskStore.setCurrentTask(realTaskId);
    startPolling(realTaskId);
  } catch {
    triggerMockReply(currentTaskId.value);
  }
}

function startPolling(taskId: string) {
  stopPolling();
  let seenMsgIds = new Set<string>();

  pollTimer = setInterval(async () => {
    try {
      // 拉取消息
      const msgRes = await getTaskMessages(taskId);
      const msgs: Message[] = Array.isArray(msgRes.data) ? msgRes.data : [];
      for (const m of msgs) {
        if (!seenMsgIds.has(m.id)) {
          seenMsgIds.add(m.id);
          addMsg(m);
        }
      }

      // 更新步骤状态
      updateSteps(msgs);

      // 检查任务是否完成
      const taskRes = await getTask(taskId);
      if (taskRes.data.status === "completed") {
        if (taskRes.data.final_response) {
          addMsg({
            id: generateId(),
            msg_type: "agent",
            content: taskRes.data.final_response,
            created_at: new Date().toISOString(),
          });
        }
        taskStore.isRunning = false;
        stopPolling();
      } else if (taskRes.data.status === "error" || taskRes.data.status === "cancelled") {
        taskStore.isRunning = false;
        stopPolling();
      }
    } catch {
      // 静默重试
    }
  }, 2000);
}

function updateSteps(msgs: Message[]) {
  const nodeMap: Record<string, number> = {
    "classify": 0, "retrieve": 1, "analysis": 2,
    "modeling": 3, "solving": 4, "verification": 5, "writing": 6,
  };
  for (const m of msgs) {
    if (typeof m.content === "string") {
      for (const [key, idx] of Object.entries(nodeMap)) {
        if (m.content.includes(key)) {
          agentSteps.value[idx].status = "done";
        }
      }
    }
  }
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
}

function triggerMockReply(taskId: string) {
  if (!replyIndex[taskId]) replyIndex[taskId] = 0;
  const replies = mockReplies[currentMode.value] || mockReplies.execute;
  const idx = replyIndex[taskId]++ % replies.length;

  // 更新步骤
  if (currentMode.value === "execute") {
    agentSteps.value.forEach((s, i) => { s.status = i < 7 ? "done" : "wait"; });
  }

  setTimeout(() => {
    addMsg({ id: generateId(), msg_type: "agent", content: replies[idx], created_at: new Date().toISOString() });
    taskStore.isRunning = false;
  }, 1000);
}

onMounted(() => {
  welcomeMode.value = (route.query.mode as "teach" | "execute") || "teach";
});

onUnmounted(() => { stopPolling(); });
</script>

<style scoped>
.slide-right-enter-active, .slide-right-leave-active { transition: width 0.3s ease, opacity 0.2s ease; }
.slide-right-enter-from, .slide-right-leave-to { width: 0 !important; opacity: 0; overflow: hidden; }
</style>
