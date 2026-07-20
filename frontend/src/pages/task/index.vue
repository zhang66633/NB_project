<template>
  <div class="flex h-full bg-background">
    <!-- 左:任务文件侧栏 -->
    <div class="w-64 shrink-0 border-r bg-background flex flex-col">
      <div class="flex h-14 items-center gap-2 border-b px-4 shrink-0">
        <button
          class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-accent transition-colors"
          @click="router.back()"
        >
          <ArrowLeft class="h-4 w-4" />
        </button>
        <span class="font-display text-sm font-medium">任务文件</span>
      </div>

      <div class="flex-1 overflow-y-auto p-3">
        <Files
          :files="uploadedFiles"
          :uploading="uploading"
          @upload="handleUpload"
          @remove="handleRemoveFile"
        />
      </div>
    </div>

    <!-- 中:对话 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 任务工具条:§标记 + 衬线标题 + 等宽模式标签(无彩色 badge) -->
      <div class="flex h-14 items-center justify-between border-b px-5 gap-3 shrink-0">
        <div class="flex items-baseline gap-3 min-w-0">
          <span class="font-mono text-xs text-primary shrink-0">§3</span>
          <h2 class="font-display text-sm font-medium truncate">
            {{ task?.title || `任务 ${task_id}` }}
          </h2>
          <span
            v-if="task?.mode"
            class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground shrink-0"
          >
            {{ task.mode === 'execute' ? '方案输出' : '教学' }}
          </span>
        </div>

        <button
          v-if="isRunning"
          class="inline-flex items-center gap-1.5 rounded-md border border-destructive/30 px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors"
          @click="cancelTask"
        >
          <StopCircle class="h-3.5 w-3.5" />
          取消
        </button>
      </div>

      <!-- 加载 -->
      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
      </div>

      <!-- 对话区 -->
      <div v-else class="flex-1 min-h-0">
        <ChatArea :task-id="task_id" />
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
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, StopCircle, Loader2 } from "lucide-vue-next";
import Files from "@/components/Files.vue";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useTaskStore } from "@/stores/task";
import * as commonApi from "@/apis/commonApi";
import * as filesApi from "@/apis/filesApi";

const props = defineProps<{
  task_id: string;
}>();

const router = useRouter();
const taskStore = useTaskStore();

const loading = ref(true);
const isRunning = ref(false);
const uploading = ref(false);
const task = ref<{ title?: string; mode?: string } | null>(null);

const uploadedFiles = ref<Array<{ name: string; size: number }>>([]);

const notebookCells = ref<Array<{ cell_type: string; source?: string }>>([]);

const steps = ref([
  { id: "1", label: "问题分析", status: "wait" as const, description: "理解题意,提取关键信息" },
  { id: "2", label: "模型构建", status: "wait" as const, description: "选择或设计数学模型" },
  { id: "3", label: "求解计算", status: "wait" as const, description: "编写求解代码,执行计算" },
  { id: "4", label: "验证分析", status: "wait" as const, description: "模型验证与鲁棒性分析" },
  { id: "5", label: "论文写作", status: "wait" as const, description: "生成规范论文" },
]);

async function fetchTask() {
  loading.value = true;
  try {
    const res = await commonApi.getTask(props.task_id);
    task.value = res.data;
  } catch {
    // Task may not exist yet, that's ok
  } finally {
    loading.value = false;
  }
}

async function cancelTask() {
  try {
    await commonApi.cancelTask(props.task_id);
    isRunning.value = false;
  } catch (e) {
    console.error("Failed to cancel task:", e);
  }
}

async function handleUpload(files: File[]) {
  uploading.value = true;
  try {
    for (const file of files) {
      await filesApi.uploadFile(file);
      uploadedFiles.value.push({ name: file.name, size: file.size });
    }
  } catch (e) {
    console.error("Upload failed:", e);
  } finally {
    uploading.value = false;
  }
}

function handleRemoveFile(name: string) {
  uploadedFiles.value = uploadedFiles.value.filter((f) => f.name !== name);
}

onMounted(() => {
  fetchTask();
  if (props.task_id && props.task_id !== "0") {
    taskStore.connectWebSocket(props.task_id);
  }
});

onUnmounted(() => {
  taskStore.closeWebSocket();
});
</script>
