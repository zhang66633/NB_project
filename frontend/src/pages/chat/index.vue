<template>
  <div class="flex h-screen bg-background">
    <!-- Sidebar -->
    <AppSidebar :collapsed="sidebarCollapsed" />

    <!-- Main content -->
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

          <div v-if="activeTaskId" class="flex items-center gap-2">
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
            v-if="rightPanelOpen !== undefined"
            class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
            @click="rightPanelOpen = !rightPanelOpen"
          >
            <PanelRight class="h-4 w-4" />
          </button>
        </div>
      </header>

      <!-- Welcome screen (no active task) -->
      <div v-if="!activeTaskId" class="flex-1 flex items-center justify-center">
        <div class="w-full max-w-2xl px-6 text-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mx-auto mb-6">
            <MessageSquare class="h-8 w-8 text-primary" />
          </div>
          <h2 class="text-2xl font-bold mb-2">开始建模对话</h2>
          <p class="text-muted-foreground mb-8">
            输入你的数学建模问题，智能体将开始协同工作
          </p>

          <div class="rounded-2xl border bg-card p-6 shadow-sm">
            <textarea
              v-model="welcomeProblem"
              rows="4"
              placeholder="描述你的建模问题..."
              class="w-full resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
                class="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
                :disabled="!welcomeProblem.trim()"
                @click="startNewTask"
              >
                <Send class="h-4 w-4 mr-1.5" />
                开始
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Chat + Right Panel -->
      <div v-else class="flex flex-1 min-h-0">
        <!-- Chat area -->
        <div class="flex-1 min-w-0 relative">
          <ChatArea :task-id="activeTaskId" />
        </div>

        <!-- Right panel -->
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
import { useRoute, useRouter } from "vue-router";
import {
  PanelLeft,
  PanelRight,
  MessageSquare,
  Send,
} from "lucide-vue-next";
import AppSidebar from "@/components/AppSidebar.vue";
import ServiceStatus from "@/components/ServiceStatus.vue";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useTaskStore } from "@/stores/task";

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();

const sidebarCollapsed = ref(false);
const rightPanelOpen = ref(true);

const welcomeProblem = ref("");
const welcomeMode = ref<"teach" | "execute">("teach");

const modeOptions = [
  { label: "教学模式", value: "teach" as const },
  { label: "方案输出", value: "execute" as const },
];

const activeTaskId = computed(() => taskStore.currentTaskId);
const taskTitle = ref("");
const currentMode = ref<"teach" | "execute">("teach");

const agentSteps = ref([
  { id: "1", label: "问题分析", status: "wait" as const, description: "理解题意，提取关键信息" },
  { id: "2", label: "模型构建", status: "wait" as const, description: "选择或设计数学模型" },
  { id: "3", label: "求解计算", status: "wait" as const, description: "编写求解代码，执行计算" },
  { id: "4", label: "验证分析", status: "wait" as const, description: "模型验证与鲁棒性分析" },
  { id: "5", label: "论文写作", status: "wait" as const, description: "生成规范论文" },
]);

const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);

function startNewTask() {
  if (!welcomeProblem.value.trim()) return;
  const mode = welcomeMode.value;
  // Set up the chat context and navigate
  router.push({
    path: "/chat",
    query: { problem: welcomeProblem.value, mode },
  });
}

onMounted(() => {
  const problem = route.query.problem as string;
  const mode = (route.query.mode as string) || "teach";
  if (problem) {
    welcomeProblem.value = problem;
    welcomeMode.value = mode as "teach" | "execute";
  }
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
