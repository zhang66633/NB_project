<template>
  <div class="flex h-screen bg-background">
    <AppSidebar :collapsed="sidebarCollapsed" />

    <div class="flex flex-1 flex-col min-w-0">
      <!-- Top bar -->
      <header class="flex h-14 items-center justify-between border-b px-4 gap-3">
        <div class="flex items-center gap-3">
          <button
            class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
            @click="sidebarCollapsed = !sidebarCollapsed"
          >
            <PanelLeft class="h-4 w-4" />
          </button>

          <div v-if="hasStarted" class="flex items-center gap-2">
            <h2 class="text-sm font-semibold truncate max-w-[200px]">
              {{ taskTitle || '建模任务' }}
            </h2>
            <span
              class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
              :class="currentMode === 'execute' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'"
            >
              {{ currentMode === 'execute' ? '方案输出' : '教学' }}
            </span>
          </div>
          <span v-else class="text-sm font-semibold">新对话</span>
        </div>

        <div class="flex items-center gap-3">
          <ServiceStatus />
          <button
            v-if="hasStarted"
            class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
            @click="rightPanelOpen = !rightPanelOpen"
          >
            <PanelRight class="h-4 w-4" />
          </button>
        </div>
      </header>

      <!-- Welcome screen -->
      <div v-if="!hasStarted" class="flex-1 flex items-center justify-center">
        <div class="w-full max-w-2xl px-6 text-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mx-auto mb-6">
            <MessageSquare class="h-8 w-8 text-primary" />
          </div>
          <h2 class="text-2xl font-bold mb-2">
            {{ welcomeMode === 'teach' ? '教学模式' : '方案输出模式' }}
          </h2>
          <p class="text-muted-foreground mb-8">
            {{ welcomeMode === 'teach' ? '苏格拉底式引导，逐步培养建模思维' : '结构化输出完整建模方案' }}
          </p>

          <div class="rounded-2xl border bg-card p-6 shadow-sm">
            <textarea
              v-model="welcomeProblem"
              rows="4"
              placeholder="描述你的建模问题（选填，进入后可继续输入）..."
              class="w-full resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              @keydown.ctrl.enter="startConversation"
            />
            <div class="flex items-center justify-between mt-3">
              <div class="flex items-center gap-2">
                <button
                  v-for="mode in modeOptions"
                  :key="mode.value"
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
                  :class="welcomeMode === mode.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-accent'"
                  @click="welcomeMode = mode.value"
                >
                  {{ mode.label }}
                </button>
              </div>
              <button
                class="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
                @click="startConversation"
              >
                <MessageSquare class="h-4 w-4 mr-1.5" />
                进入对话
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat + Right Panel -->
      <div v-else class="flex flex-1 min-h-0">
        <div class="flex-1 min-w-0 relative">
          <ChatArea :task-id="currentTaskId" @send="handleUserSend" />
        </div>

        <Transition name="slide-right">
          <div
            v-if="rightPanelOpen"
            class="w-80 border-l bg-background flex flex-col overflow-hidden"
          >
            <div class="border-b px-4 py-2 bg-muted/30">
              <span class="text-xs font-medium text-muted-foreground">执行进度</span>
            </div>
            <div class="flex-1 overflow-y-auto p-4">
              <UserStepper :steps="agentSteps" />
            </div>
            <div class="flex-1 border-t overflow-hidden">
              <NotebookArea :cells="notebookCells" />
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  PanelLeft,
  PanelRight,
  MessageSquare,
} from "lucide-vue-next";
import AppSidebar from "@/components/AppSidebar.vue";
import ServiceStatus from "@/components/ServiceStatus.vue";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useTaskStore } from "@/stores/task";
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
const taskTitle = ref("");

const modeOptions = [
  { label: "教学模式", value: "teach" as const },
  { label: "方案输出", value: "execute" as const },
];

const agentSteps = ref([
  { id: "1", label: "问题分析", status: "wait" as const, description: "理解题意，提取关键信息" },
  { id: "2", label: "模型构建", status: "wait" as const, description: "选择或设计数学模型" },
  { id: "3", label: "求解计算", status: "wait" as const, description: "编写求解代码，执行计算" },
  { id: "4", label: "验证分析", status: "wait" as const, description: "模型验证与鲁棒性分析" },
  { id: "5", label: "论文写作", status: "wait" as const, description: "生成规范论文" },
]);

const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);

function generateId() {
  return `task_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function startConversation() {
  const taskId = generateId();
  currentTaskId.value = taskId;
  currentMode.value = welcomeMode.value;
  hasStarted.value = true;
  taskTitle.value = welcomeProblem.value.trim()
    ? welcomeProblem.value.slice(0, 30) + "..."
    : "新对话";

  taskStore.setCurrentTask(taskId);

  // If there's a problem, add it as the first user message
  if (welcomeProblem.value.trim()) {
    const userMsg: Message = {
      id: generateId(),
      msg_type: "user",
      content: welcomeProblem.value.trim(),
      created_at: new Date().toISOString(),
    };
    taskStore.appendMessage(taskId, userMsg);
  }
}

function handleUserSend(text: string) {
  if (!currentTaskId.value) return;
  const userMsg: Message = {
    id: generateId(),
    msg_type: "user",
    content: text,
    created_at: new Date().toISOString(),
  };
  taskStore.appendMessage(currentTaskId.value, userMsg);
}

onMounted(() => {
  const mode = (route.query.mode as string) || "teach";
  welcomeMode.value = mode as "teach" | "execute";
});
</script>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: width 0.3s ease, opacity 0.2s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  width: 0 !important;
  opacity: 0;
  overflow: hidden;
}
</style>
