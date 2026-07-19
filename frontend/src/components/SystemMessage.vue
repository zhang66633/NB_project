<template>
  <div
    :class="[
      'flex items-start gap-3 rounded-lg p-3 text-sm',
      bgClass,
    ]"
  >
    <component :is="icon" class="h-5 w-5 shrink-0 mt-0.5" :class="iconClass" />
    <div class="flex-1 min-w-0">
      <p v-if="title" class="font-medium mb-0.5" :class="titleClass">{{ title }}</p>
      <p :class="textClass">{{ message.content }}</p>
      <p v-if="message.created_at" class="text-xs mt-1 opacity-60">
        {{ formatTime(message.created_at) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  Info,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-vue-next";
import type { SystemMessage as SysMsg } from "@/utils/response";

const props = defineProps<{
  message: SysMsg;
}>();

const config = computed(() => {
  switch (props.message.type) {
    case "success":
      return {
        icon: CheckCircle2,
        bg: "bg-green-50 border border-green-200 dark:bg-green-950/30 dark:border-green-800",
        iconColor: "text-green-500",
        titleColor: "text-green-800 dark:text-green-300",
        textColor: "text-green-700 dark:text-green-400",
        defaultTitle: "成功",
      };
    case "warning":
      return {
        icon: AlertTriangle,
        bg: "bg-yellow-50 border border-yellow-200 dark:bg-yellow-950/30 dark:border-yellow-800",
        iconColor: "text-yellow-500",
        titleColor: "text-yellow-800 dark:text-yellow-300",
        textColor: "text-yellow-700 dark:text-yellow-400",
        defaultTitle: "警告",
      };
    case "error":
      return {
        icon: XCircle,
        bg: "bg-red-50 border border-red-200 dark:bg-red-950/30 dark:border-red-800",
        iconColor: "text-red-500",
        titleColor: "text-red-800 dark:text-red-300",
        textColor: "text-red-700 dark:text-red-400",
        defaultTitle: "错误",
      };
    default:
      return {
        icon: Info,
        bg: "bg-blue-50 border border-blue-200 dark:bg-blue-950/30 dark:border-blue-800",
        iconColor: "text-blue-500",
        titleColor: "text-blue-800 dark:text-blue-300",
        textColor: "text-blue-700 dark:text-blue-400",
        defaultTitle: "信息",
      };
  }
});

const icon = computed(() => config.value.icon);
const bgClass = computed(() => config.value.bg);
const iconClass = computed(() => config.value.iconColor);
const titleClass = computed(() => config.value.titleColor);
const textClass = computed(() => config.value.textColor);
const title = computed(() => config.value.defaultTitle);

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
</script>
