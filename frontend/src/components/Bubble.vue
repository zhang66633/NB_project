<template>
  <div class="flex gap-3 w-full my-2 animate-in fade-in slide-in-from-bottom-2">
    <div v-if="!isUser" class="flex flex-col items-center shrink-0">
      <div class="flex h-8 w-8 items-center justify-center rounded-sm border border-border">
        <span class="font-display text-xs font-medium leading-none">{{ avatarLetter }}</span>
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div :class="isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'">
        <div
          :class="[
            'max-w-[calc(100%-72px)] rounded-md px-4 py-3 text-sm leading-relaxed',
            isUser
              ? 'bg-foreground text-background rounded-br-sm'
              : 'border border-border bg-background text-foreground rounded-bl-sm',
          ]"
        >
          <div v-if="isAgent && agentLabel" class="mb-1.5">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">[{{ agentLabel }}]</span>
          </div>

          <div v-if="isTool" class="space-y-1">
            <div class="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              <Wrench class="h-3 w-3" />
              <span>调用工具: {{ toolName }}</span>
            </div>
            <div v-if="toolInput" class="text-xs text-muted-foreground font-mono bg-muted/40 rounded p-1.5 overflow-x-auto border border-border">
              {{ formatToolInput(toolInput) }}
            </div>
          </div>

          <div v-else-if="isSystem" class="flex items-center gap-2">
            <component :is="sysIcon" class="h-4 w-4 shrink-0" :class="sysColor" />
            <span class="text-xs">{{ content }}</span>
          </div>

          <div
            v-else-if="content"
            class="prose prose-sm dark:prose-invert max-w-none break-words"
            :class="{ 'cursor-pointer': isTyping }"
            v-html="renderedContent"
            @click="isTyping && skip()"
          />

          <div v-else class="flex items-center gap-1.5 py-1">
            <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 0ms" />
            <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 150ms" />
            <span class="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style="animation-delay: 300ms" />
          </div>

        </div>
        <span v-if="timestamp" class="font-mono text-[10px] text-muted-foreground/50 mt-0.5">{{ timestamp }}</span>
      </div>
    </div>

    <div v-if="isUser" class="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-border">
      <span class="font-display text-xs font-medium leading-none">U</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
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
import { useTypewriter } from "@/composables/useTypewriter";

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

// 打字机仅用于「非流式的一次性外部消息」。
// 我们流式生成的消息（streaming 字段存在，无论 true/false）已实时逐字展示过，
// 切回历史后不应再重放，否则造成闪烁/重复。
const enableTypewriter = computed(
  () =>
    props.isLast &&
    isAgent.value &&
    !("streaming" in props.message),
);
const rawText = ref(content.value);

const { displayText, isTyping, skip } = useTypewriter(rawText, 12, enableTypewriter);

watch(content, (val) => {
  rawText.value = val;
}, { immediate: true });

const agentLabel = computed(() => {
  if (!isAgent.value) return "";
  const agentType = (props.message as AgentMessage).agent_type;
  if (!agentType) return "";
  const labels: Record<string, string> = {
    [AgentType.ORCHESTRATOR]: "主控",
    [AgentType.ANALYSIS]: "分析",
    [AgentType.MODELING]: "建模",
    [AgentType.SOLVING]: "求解",
    [AgentType.VERIFICATION]: "验证",
    [AgentType.WRITING]: "写作",
  };
  return labels[agentType] ?? agentType;
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

// 对带 LaTeX 的流式内容，流式期间每次全量 parse 可能渲染半个公式。
// 直接 parse 全量文本即可——marked 对不完整 $...$ 会按原样输出，不会报错。
const renderedContent = computed(() => {
  const text = enableTypewriter.value ? displayText.value : content.value;
  if (!text) return "";
  return marked.parse(text) as string;
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
