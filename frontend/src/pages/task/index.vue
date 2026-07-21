<template>
  <div class="flex h-full bg-background">
    <!-- 左:任务文件 -->
    <div class="w-64 shrink-0 border-r bg-background flex flex-col">
      <div class="flex h-14 items-center gap-2 border-b px-4 shrink-0">
        <button class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-accent transition-colors" @click="router.back()">
          <ArrowLeft class="h-4 w-4" />
        </button>
        <span class="font-display text-sm font-medium">任务文件</span>
      </div>
      <div class="flex-1 overflow-y-auto p-3">
        <Files :files="uploadedFiles" :uploading="uploading" @upload="handleUpload" @remove="handleRemoveFile" />
      </div>
    </div>

    <!-- 中:对话 -->
    <div class="flex-1 flex flex-col min-w-0">
      <div class="flex h-14 items-center justify-between border-b px-5 gap-3 shrink-0">
        <div class="flex items-baseline gap-3 min-w-0">
          <span class="font-mono text-xs text-primary shrink-0">§3</span>
          <h2 class="font-display text-sm font-medium truncate">{{ session?.title || `任务 ${task_id}` }}</h2>
          <span class="font-mono text-[10px] uppercase tracking-wider shrink-0"
            :class="currentMode === 'teach' ? 'text-green-600/70' : 'text-blue-600/70'">
            {{ currentMode === 'teach' ? '教学' : '方案输出' }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <!-- 模式切换 -->
          <button
            class="font-mono text-[10px] text-muted-foreground hover:text-foreground transition-colors"
            @click="toggleMode"
          >
            {{ currentMode === 'teach' ? '切方案' : '切教学' }}
          </button>
          <button
            v-if="isRunning"
            class="inline-flex items-center gap-1.5 rounded-md border border-destructive/30 px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors"
            @click="cancelTask"
          >
            <StopCircle class="h-3.5 w-3.5" />取消
          </button>
        </div>
      </div>

      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
      </div>

      <div v-else class="flex-1 min-h-0">
        <ChatArea
          :task-id="task_id"
          :messages="displayMessages"
          @send="handleUserSend"
        />
      </div>
    </div>

    <!-- 右:执行进度 + 笔记 -->
    <div class="w-80 shrink-0 border-l bg-background flex flex-col overflow-hidden">
      <div class="border-b px-4 py-3 shrink-0">
        <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 执行进度</span>
      </div>
      <div class="flex-1 overflow-y-auto p-3">
        <UserStepper :steps="steps" />
      </div>
      <div class="flex-1 border-t overflow-hidden flex flex-col">
        <div class="border-b px-4 py-2 shrink-0">
          <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 笔记</span>
        </div>
        <NotebookArea :cells="notebookCells" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, StopCircle, Loader2 } from "lucide-vue-next";
import Files from "@/components/Files.vue";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import { useTaskStore } from "@/stores/task";
import * as commonApi from "@/apis/commonApi";
import * as filesApi from "@/apis/filesApi";
import type { Message } from "@/utils/response";

const props = defineProps<{ task_id: string }>();
const router = useRouter();
const chatSession = useChatSessionStore();
const taskStore = useTaskStore();

const loading = ref(true);
const uploading = ref(false);
const task = ref<{ title?: string; mode?: string } | null>(null);
const currentMode = ref<"teach" | "execute">("teach");
const uploadedFiles = ref<Array<{ name: string; size: number }>>([]);
const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);

const session = ref(chatSession.sessions.find((s) => s.id === props.task_id) || null);

// 聊天面板消息 = 用户在 chatSession 发的问题 + 后端经 WS 推送的 agent 进度/最终答案
const displayMessages = computed<Message[]>(() => {
  const userMsgs = chatSession.sessions.find((s) => s.id === props.task_id)?.messages ?? [];
  const agentMsgs = taskStore.messages;
  return [...userMsgs, ...agentMsgs];
});

// 运行态来自 WS（taskStore.isRunning），不再用本地 mock
const isRunning = computed(() => taskStore.isRunning);

// 根据当前阶段高亮右侧步骤条
const stepOrder = ["问题分析", "模型构建", "求解计算", "验证分析", "论文写作"];
const steps = computed(() => {
  const current = taskStore.currentStep;
  const idx = stepOrder.indexOf(current);
  return stepOrder.map((label, i) => ({
    id: String(i + 1),
    label,
    status: idx === -1 ? ("wait" as const) : (i < idx ? ("done" as const) : i === idx ? ("active" as const) : ("wait" as const)),
    description: {
      "问题分析": "识别问题类型,理解题意",
      "模型构建": "选择并建立数学模型",
      "求解计算": "生成并执行求解代码",
      "验证分析": "检验模型鲁棒性",
      "论文写作": "生成结构化论文",
    }[label] as string,
  }));
});
  { id: "1", label: "问题分析", status: "wait" as const, description: "苏格拉底式引导,理解题意" },
  { id: "2", label: "模型构建", status: "wait" as const, description: "启发式选择数学模型" },
  { id: "3", label: "求解计算", status: "wait" as const, description: "引导编写求解代码" },
  { id: "4", label: "验证分析", status: "wait" as const, description: "自查模型鲁棒性" },
  { id: "5", label: "论文写作", status: "wait" as const, description: "生成结构化论文框架" },
]);

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function toggleMode() {
  currentMode.value = currentMode.value === "teach" ? "execute" : "teach";
}

function handleUserSend(text: string) {
  if (!session.value) return;

  // 用户问题写入会话（用于聊天面板显示）
  const userMsg: Message = { id: generateId(), msg_type: "user", content: text, created_at: new Date().toISOString() };
  chatSession.addMessage(props.task_id, userMsg);

  // 发起后端真实任务（WebSocket 会推送进度与最终答案）
  commonApi.createTask({ problem: text, mode: currentMode.value })
    .catch((e) => {
      console.error("createTask failed", e);
      // 后端不可达时给一个提示气泡，不再走 mock 假数据
      chatSession.addMessage(props.task_id, {
        id: generateId(), msg_type: "agent",
        content: "⚠️ 后端服务暂不可达，请确认后端已启动（uvicorn app.main:app --port 8000）。",
        created_at: new Date().toISOString(),
      });
    });
}

async function fetchTask() {
  loading.value = true;
  try {
    const res = await commonApi.getTask(props.task_id);
    task.value = res.data;
    if (res.data.mode) currentMode.value = res.data.mode;
  } catch { /* ok */ }
  finally { loading.value = false; }
}

async function cancelTask() {
  try { await commonApi.cancelTask(props.task_id); isRunning.value = false; }
  catch (e) { console.error(e); }
}

async function handleUpload(files: File[]) {
  uploading.value = true;
  try {
    for (const file of files) {
      await filesApi.uploadFile(file);
      uploadedFiles.value.push({ name: file.name, size: file.size });
    }
  } catch (e) { console.error(e); }
  finally { uploading.value = false; }
}

function handleRemoveFile(name: string) {
  uploadedFiles.value = uploadedFiles.value.filter((f) => f.name !== name);
}

onMounted(() => {
  fetchTask();
  // 创建/更新任务会话记录
  const title = task.value?.title || `任务 ${props.task_id}`;
  chatSession.createTaskSession(props.task_id, title, "teach");
  session.value = chatSession.sessions.find((s) => s.id === props.task_id) || null;

  if (props.task_id && props.task_id !== "0") {
    taskStore.connectWebSocket(props.task_id);
  }
});

onUnmounted(() => {
  taskStore.closeWebSocket();
});
</script>
