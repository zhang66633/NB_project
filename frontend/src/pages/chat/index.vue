<template>
  <div class="flex h-full bg-background">
    <!-- Welcome:学术手稿式,左对齐,§章节标记,衬线标题,无彩色图标方块 -->
    <div v-if="!hasStarted" class="flex-1 overflow-y-auto bg-grid-paper">
      <div class="mx-auto max-w-3xl px-6 sm:px-10 py-20 sm:py-28">
        <p class="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground mb-6">
          §2 &nbsp; 对话
        </p>
        <h2 class="font-display text-4xl sm:text-5xl font-medium tracking-tight leading-[1.05]">
          {{ welcomeMode === 'teach' ? '引导式建模' : '结构化输出' }}
        </h2>
        <p class="font-display italic text-xl sm:text-2xl text-muted-foreground mt-3 leading-[1.2] pb-1">
          {{ welcomeMode === 'teach' ? '先想后给,留下推理痕迹' : '从问题到论文,一次成型' }}
        </p>
        <p class="mt-6 text-sm text-muted-foreground max-w-xl leading-relaxed">
          {{ welcomeMode === 'teach'
            ? '描述你遇到的问题,智能体以提问引导你逐步建立建模思维。'
            : '描述你遇到的问题,智能体输出完整建模方案、代码与论文。' }}
        </p>

        <!-- 模式切换:等宽小标签,非胶囊填充 -->
        <div class="mt-10 flex items-center gap-5">
          <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">模式</span>
          <button
            v-for="mode in modeOptions"
            :key="mode.value"
            class="font-mono text-xs transition-colors"
            :class="welcomeMode === mode.value ? 'text-primary' : 'text-muted-foreground/60 hover:text-foreground'"
            @click="welcomeMode = mode.value"
          >
            {{ mode.label }}
          </button>
        </div>

        <!-- 问题输入:细线边框,无卡片包裹 -->
        <div class="mt-6">
          <textarea
            v-model="welcomeProblem"
            rows="5"
            placeholder="例如:某物流公司需在 5 个备选地点中选 2 个建配送中心,最小化总运输成本..."
            class="w-full resize-none rounded-md border border-border bg-background px-4 py-3 text-sm leading-relaxed placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @keydown.ctrl.enter="startConversation"
          />
          <div class="mt-3 flex items-center justify-between">
            <span class="font-mono text-[10px] text-muted-foreground/70">⌘+Enter 提交</span>
            <button
              class="group inline-flex items-center gap-2 rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background transition-transform hover:scale-[0.98] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              @click="startConversation"
            >
              进入对话
              <ArrowRight class="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat:已开始对话 -->
    <div v-else class="flex flex-1 min-h-0">
      <div class="flex-1 min-w-0 relative">
        <button
          v-if="hasStarted"
          class="absolute top-2 right-2 z-10 inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-background/80 backdrop-blur hover:bg-accent transition-colors"
          title="切换执行进度面板"
          @click="rightPanelOpen = !rightPanelOpen"
        >
          <PanelRight class="h-4 w-4" />
        </button>
        <ChatArea :task-id="currentTaskId" @send="handleUserSend" />
      </div>
      <Transition name="slide-right">
        <div v-if="rightPanelOpen" class="w-80 shrink-0 border-l bg-background flex flex-col overflow-hidden">
          <div class="border-b px-4 py-3">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 执行进度</span>
          </div>
          <div class="flex-1 overflow-y-auto p-4"><UserStepper :steps="agentSteps" /></div>
          <div class="flex-1 border-t overflow-hidden">
            <div class="border-b px-4 py-2">
              <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 笔记</span>
            </div>
            <NotebookArea :cells="notebookCells" />
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { PanelRight, ArrowRight } from "lucide-vue-next";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useTaskStore } from "@/stores/task";
import { createTask, getTaskMessages, getTask } from "@/apis/commonApi";
import type { Message } from "@/utils/response";

const route = useRoute();
const taskStore = useTaskStore();

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
  { id: "5", label: "求解计算", status: "wait" as const, description: "编写代码,执行计算" },
  { id: "6", label: "验证分析", status: "wait" as const, description: "模型验证与鲁棒性分析" },
  { id: "7", label: "论文写作", status: "wait" as const, description: "生成规范论文" },
]);

const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);
let pollTimer: ReturnType<typeof setInterval> | null = null;

const mockReplies: Record<string, string[]> = {
  teach: [
    "🤔 **让我们一起来分析这个问题。**\n\n首先,你能尝试回答:这个问题的**核心目标**是什么?是最大化某个量,还是最小化?",
    "📝 **很好!下一步我们来看决策变量。**\n\n在这个问题中,哪些因素的值是我们可以决定的?",
    "💡 **现在考虑约束条件。**\n\n我们的决策受到哪些现实条件的限制?试着至少列出 3 条约束。",
  ],
  execute: [
    "📋 **已提交建模任务,智能体正在分析中...**\n\n正在启动多智能体编排流程。后端处理完成后结果将自动显示。",
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

  const localId = generateId();
  currentTaskId.value = localId;
  hasStarted.value = true;
  taskStore.setCurrentTask(localId);

  addUserMsg(problem);
  taskStore.isRunning = true;

  try {
    const res = await createTask({ problem, mode: welcomeMode.value });
    const realTaskId = res.data.task_id;
    currentTaskId.value = realTaskId;
    taskStore.setCurrentTask(realTaskId);
    startPolling(realTaskId);
  } catch {
    console.warn("后端不可用,使用模拟回复");
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
      const msgRes = await getTaskMessages(taskId);
      const msgs: Message[] = Array.isArray(msgRes.data) ? msgRes.data : [];
      for (const m of msgs) {
        if (!seenMsgIds.has(m.id)) {
          seenMsgIds.add(m.id);
          addMsg(m);
        }
      }
      updateSteps(msgs);

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
