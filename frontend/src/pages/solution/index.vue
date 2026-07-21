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
        :messages="chatSession.activeSolutionMessages"
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
          <div v-if="progressOpen" class="p-4"><UserStepper :steps="agentSteps" /></div>
        </div>

        <div v-if="paperReady">
          <div class="border-b border-border px-4 py-2 flex items-center justify-between cursor-pointer hover:bg-accent/50" @click="paperSectionOpen = !paperSectionOpen">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 论文</span>
            <div class="flex items-center gap-1.5">
              <div class="flex gap-1.5 mr-1">
                <button class="font-mono text-[10px] text-primary hover:underline" @click.stop="showPaper = !showPaper">
                  {{ showPaper ? '收起' : '查看' }}
                </button>
                <button class="font-mono text-[10px] text-primary hover:underline" @click.stop="downloadPaper">下载 .tex</button>
              </div>
              <ChevronDown class="h-3 w-3 text-muted-foreground transition-transform" :class="{ 'rotate-180': paperSectionOpen }" />
            </div>
          </div>
          <div v-if="paperSectionOpen && showPaper" class="p-3">
            <pre class="text-[11px] font-mono leading-relaxed whitespace-pre-wrap text-muted-foreground">{{ paperContent }}</pre>
          </div>
        </div>

        <div>
          <div class="border-b border-border px-4 py-2 flex items-center justify-between cursor-pointer hover:bg-accent/50" @click="notesOpen = !notesOpen">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 笔记</span>
            <ChevronDown class="h-3 w-3 text-muted-foreground transition-transform" :class="{ 'rotate-180': notesOpen }" />
          </div>
          <div v-if="notesOpen" class="overflow-hidden"><NotebookArea :cells="notebookCells" /></div>
        </div>
      </div>
    </Transition>
    <Teleport to="body">
      <div v-if="paperFullscreen" class="fixed inset-0 z-50 bg-background/95 backdrop-blur flex flex-col" @keydown.escape="paperFullscreen = false">
        <div class="flex items-center justify-between px-6 py-3 border-b">
          <span class="font-mono text-xs tracking-wider text-muted-foreground">LaTeX 论文</span>
          <div class="flex gap-3">
            <button class="font-mono text-xs text-primary hover:underline" @click="downloadPaper">下载 .tex</button>
            <button class="font-mono text-xs text-muted-foreground hover:text-foreground" @click="paperFullscreen = false">关闭</button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full">
          <pre class="text-sm font-mono leading-relaxed whitespace-pre-wrap">{{ paperContent }}</pre>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { PanelRight, ChevronDown } from "lucide-vue-next";
import ChatArea from "@/components/ChatArea.vue";
import UserStepper from "@/components/UserStepper.vue";
import NotebookArea from "@/components/NotebookArea.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import { createTask } from "@/apis/commonApi";
import type { Message } from "@/utils/response";

const chatSession = useChatSessionStore();

const rightPanelOpen = ref(true);
const progressOpen = ref(true);
const paperSectionOpen = ref(true);
const notesOpen = ref(true);

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

const paperReady = ref(false);
const showPaper = ref(false);
const paperContent = ref("");
const paperFullscreen = ref(false);

const mockReplies = [
  "📋 **已提交建模任务，智能体正在分析中...**\n\n正在启动多智能体编排流程。后端处理完成后结果将自动显示。",
];

let replyIndex = 0;

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function triggerMockReply(sessionId: string) {
  if (replyIndex < mockReplies.length) {
    const reply: Message = {
      id: generateId(),
      msg_type: "agent",
      content: mockReplies[replyIndex],
      created_at: new Date().toISOString(),
    };
    chatSession.addMessage("solution", sessionId, reply);
    replyIndex++;
  }
  chatSession.isRunning = false;
}

function handleUserSend(text: string) {
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

  const existingMessages = chatSession.activeSolutionMessages;
  const hasAgentReply = existingMessages.some((m) => m.msg_type === "agent");
  if (hasAgentReply && existingMessages[existingMessages.length - 1].msg_type !== "user") {
    chatSession.isRunning = false;
    return;
  }

  createTask({ problem: text, mode: "execute" })
    .then(() => {
      triggerMockReply(sessionId);
    })
    .catch(() => {
      triggerMockReply(sessionId);
    });
}

function downloadPaper() {
  const blob = new Blob([paperContent.value], { type: "text/x-tex" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "math-model-paper.tex";
  a.click();
  URL.revokeObjectURL(url);
}

onMounted(() => {
  if (!chatSession.activeSolutionId && chatSession.sortedSolutionSessions.length > 0) {
    chatSession.switchSession("solution", chatSession.sortedSolutionSessions[0].id);
  }
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
