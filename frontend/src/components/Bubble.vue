<template>
  <div
    :class="[
      'flex gap-3 my-2 animate-in fade-in slide-in-from-bottom-2',
      isUser ? 'justify-end' : 'justify-start',
    ]"
  >
    <!-- Agent/System Avatar -->
    <div
      v-if="!isUser"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
      :class="avatarClass"
    >
      <component :is="avatarIcon" class="h-4 w-4" />
    </div>

    <!-- Bubble -->
    <div
      :class="[
        'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
        isUser
          ? 'bg-primary text-primary-foreground rounded-br-md'
          : 'bg-muted text-foreground rounded-bl-md',
      ]"
    >
      <!-- Agent type badge -->
      <div v-if="isAgent && agentLabel" class="mb-1">
        <span class="inline-flex items-center rounded-full bg-background/50 px-2 py-0.5 text-xs font-medium">
          {{ agentLabel }}
        </span>
      </div>

      <!-- Tool call message -->
      <div v-if="isTool" class="space-y-1">
        <div class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
          <Wrench class="h-3 w-3" />
          <span>调用工具: {{ toolName }}</span>
        </div>
        <div v-if="toolInput" class="text-xs text-muted-foreground font-mono bg-background/50 rounded p-1.5 overflow-x-auto">
          {{ formatToolInput(toolInput) }}
        </div>
      </div>

      <!-- System message -->
      <div v-else-if="isSystem" class="flex items-center gap-2">
        <component :is="sysIcon" class="h-4 w-4 shrink-0" :class="sysColor" />
        <span class="text-xs">{{ content }}</span>
      </div>

      <!-- Markdown content -->
      <div
        v-else-if="content"
        class="prose prose-sm dark:prose-invert max-w-none break-words"
        v-html="renderedContent"
      />

      <!-- Loading placeholder -->
      <div v-else class="flex items-center gap-1.5 py-1">
        <span class="h-2 w-2 rounded-full bg-current animate-bounce" style="animation-delay: 0ms" />
        <span class="h-2 w-2 rounded-full bg-current animate-bounce" style="animation-delay: 150ms" />
        <span class="h-2 w-2 rounded-full bg-current animate-bounce" style="animation-delay: 300ms" />
      </div>

      <!-- Timestamp -->
      <div
        :class="[
          'mt-1 text-xs',
          isUser ? 'text-primary-foreground/60' : 'text-muted-foreground',
        ]"
        v-if="timestamp"
      >
        {{ timestamp }}
      </div>
    </div>

    <!-- User Avatar -->
    <div
      v-if="isUser"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-medium"
    >
      U
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import {
  User,
  Brain,
  Wrench,
  Info,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-vue-next";
import type { Message, SystemMessage as SysMsg, AgentMessage, ToolMessage } from "@/utils/response";
import { AgentType } from "@/utils/enum";

marked.use(markedKatex({ throwOnError: false }));

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

const toolName = computed(() => {
  if (!isTool.value) return "";
  return (props.message as ToolMessage).tool_name ?? "";
});

const toolInput = computed(() => {
  if (!isTool.value) return null;
  return (props.message as ToolMessage).input;
});

const avatarClass = computed(() => {
  if (isAgent.value) return "bg-blue-100 text-blue-600";
  if (isSystem.value) return "bg-gray-100 text-gray-600";
  if (isTool.value) return "bg-purple-100 text-purple-600";
  return "bg-muted text-muted-foreground";
});

const avatarIcon = computed(() => {
  if (isAgent.value) return Brain;
  if (isSystem.value) return Info;
  if (isTool.value) return Wrench;
  return Info;
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
    case "success": return "text-green-500";
    case "warning": return "text-yellow-500";
    case "error": return "text-red-500";
    default: return "text-blue-500";
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
