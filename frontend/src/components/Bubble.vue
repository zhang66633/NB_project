<template>
  <div
    :class="[
      'flex gap-3 my-2 animate-in fade-in slide-in-from-bottom-2',
      isUser ? 'justify-end' : 'justify-start',
    ]"
  >
    <!-- Agent/System 头像:细线方框(非彩色圆),衬线首字母 -->
    <div
      v-if="!isUser"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-border"
    >
      <span class="font-display text-xs font-medium leading-none">{{ avatarLetter }}</span>
    </div>

    <!-- 气泡:rounded-md(非 2xl),用户深近黑,agent 细线 -->
    <div
      :class="[
        'max-w-[80%] rounded-md px-4 py-3 text-sm leading-relaxed',
        isUser
          ? 'bg-foreground text-background rounded-br-sm'
          : 'border border-border bg-background text-foreground rounded-bl-sm',
      ]"
    >
      <!-- Agent 类型标签:等宽小字(非彩色 badge) -->
      <div v-if="isAgent && agentLabel" class="mb-1.5">
        <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">[{{ agentLabel }}]</span>
      </div>

      <!-- 工具调用 -->
      <div v-if="isTool" class="space-y-1">
        <div class="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          <Wrench class="h-3 w-3" />
          <span>调用工具: {{ toolName }}</span>
        </div>
        <div v-if="toolInput" class="text-xs text-muted-foreground font-mono bg-muted/40 rounded p-1.5 overflow-x-auto border border-border">
          {{ formatToolInput(toolInput) }}
        </div>
      </div>

      <!-- 系统消息 -->
      <div v-else-if="isSystem" class="flex items-center gap-2">
        <component :is="sysIcon" class="h-4 w-4 shrink-0" :class="sysColor" />
        <span class="text-xs">{{ content }}</span>
      </div>

      <!-- Markdown 内容 -->
      <div
        v-else-if="content"
        class="prose prose-sm dark:prose-invert max-w-none break-words"
        v-html="renderedContent"
      />

      <!-- 加载占位 -->
      <div v-else class="flex items-center gap-1.5 py-1">
        <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 0ms" />
        <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 150ms" />
        <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 300ms" />
      </div>

      <!-- 时间戳:等宽小字 -->
      <div
        :class="[
          'mt-1.5 font-mono text-[10px]',
          isUser ? 'text-background/50' : 'text-muted-foreground/70',
        ]"
        v-if="timestamp"
      >
        {{ timestamp }}
      </div>
    </div>

    <!-- 用户头像:细线方框 + 衬线 U -->
    <div
      v-if="isUser"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-border"
    >
      <span class="font-display text-xs font-medium leading-none">U</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import {
  Wrench,
  Info,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-vue-next";
import type { Message, SystemMessage as SysMsg, AgentMessage, ToolMessage } from "@/utils/response";
import { AgentType } from "@/utils/enum";

marked.use(markedKatex({ throwOnError: false, nonStandard: true }));

const props = withDefaults(defineProps<{
  message: Message;
  isLast?: boolean;
}>(), {
  isLast: false,
});

const isUser = computed(() => props.message.msg_type === "user");
const isAgent = computed(() => props.message.msg_type === "agent");
const isSystem = computed(() => props.message.msg_type === "system");
const isTool = computed(() => props.message.msg_type === "tool");

const content = computed(() => props.message.content ?? "");

const agentLabel = computed(() => {
  if (!isAgent.value) return "";
  const agentMsg = props.message as AgentMessage;
  const labels: Record<string, string> = {
    [AgentType.ORCHESTRATOR]: "主控",
    [AgentType.ANALYSIS]: "分析",
    [AgentType.MODELING]: "建模",
    [AgentType.SOLVING]: "求解",
    [AgentType.VERIFICATION]: "验证",
    [AgentType.WRITING]: "写作",
  };
  return labels[agentMsg.agent_type] ?? agentMsg.agent_type;
});

const avatarLetter = computed(() => {
  if (isAgent.value) return "A";
  if (isSystem.value) return "S";
  if (isTool.value) return "T";
  return "A";
});

const toolName = computed(() => {
  if (!isTool.value) return "";
  return (props.message as ToolMessage).tool_name ?? "";
});

const toolInput = computed(() => {
  if (!isTool.value) return null;
  return (props.message as ToolMessage).input;
});

const sysIcon = computed(() => {
  const sys = props.message as SysMsg;
  switch (sys.type) {
    case "success": return CheckCircle2;
    case "warning": return AlertTriangle;
    case "error": return XCircle;
    default: return Info;
  }
});

const sysColor = computed(() => {
  const sys = props.message as SysMsg;
  switch (sys.type) {
    case "success": return "text-primary";
    case "warning": return "text-amber-600";
    case "error": return "text-destructive";
    default: return "text-muted-foreground";
  }
});

const renderedContent = computed(() => {
  if (!content.value) return "";
  return marked.parse(content.value) as string;
});

const timestamp = computed(() => {
  if (!props.message.created_at) return "";
  return new Date(props.message.created_at).toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });
});

function formatToolInput(input: Record<string, unknown> | null): string {
  if (!input) return "";
  try {
    return JSON.stringify(input, null, 2).slice(0, 500);
  } catch {
    return String(input);
  }
}
</script>
