<template>
  <div class="flex items-center gap-2 text-sm">
    <span
      class="relative flex h-2.5 w-2.5"
      :title="statusText"
    >
      <span
        class="absolute inline-flex h-full w-full rounded-full opacity-75"
        :class="pingColor"
        v-if="status === 'connecting' || status === 'reconnecting'"
      />
      <span
        class="relative inline-flex h-2.5 w-2.5 rounded-full"
        :class="dotColor"
      />
    </span>
    <span class="text-muted-foreground text-xs">{{ statusText }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useTaskStore } from "@/stores/task";

const taskStore = useTaskStore();

const statusText = computed(() => {
  const map: Record<string, string> = {
    connected: "已连接",
    connecting: "连接中...",
    disconnected: "未连接",
    reconnecting: "重连中...",
  };
  return map[taskStore.wsStatus] ?? "未知";
});

const dotColor = computed(() => {
  switch (taskStore.wsStatus) {
    case "connected":
      return "bg-green-500";
    case "connecting":
    case "reconnecting":
      return "bg-yellow-500";
    default:
      return "bg-red-500";
  }
});

const pingColor = computed(() => {
  switch (taskStore.wsStatus) {
    case "connecting":
      return "animate-ping bg-yellow-400";
    case "reconnecting":
      return "animate-ping bg-yellow-400";
    default:
      return "";
  }
});
</script>
