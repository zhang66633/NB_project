<template>
  <div class="flex items-center gap-2 text-sm">
    <span
      class="relative flex h-2.5 w-2.5"
      :title="statusText"
    >
      <span
        v-if="status === 'connecting' || status === 'reconnecting'"
        class="absolute inline-flex h-full w-full rounded-sm opacity-75 animate-ping"
        :class="pingColor"
      />
      <span
        class="relative inline-flex h-2.5 w-2.5 rounded-sm border"
        :class="dotClass"
      />
    </span>
    <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
      {{ statusText }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useTaskStore } from "@/stores/task";

const taskStore = useTaskStore();

const status = computed(() => taskStore.wsStatus);

const statusText = computed(() => {
  const map: Record<string, string> = {
    connected: "已连接",
    connecting: "连接中",
    disconnected: "未连接",
    reconnecting: "重连中",
  };
  return map[status.value] ?? "未知";
});

// 学术手稿:暖橙单色 + 细线方框,去掉刺眼红/绿
const dotClass = computed(() => {
  switch (status.value) {
    case "connected":
      return "border-primary bg-primary";
    case "connecting":
    case "reconnecting":
      return "border-primary bg-primary/50";
    default:
      return "border-border bg-muted";
  }
});

const pingColor = computed(() => {
  switch (status.value) {
    case "connecting":
    case "reconnecting":
      return "bg-primary/50";
    default:
      return "";
  }
});
</script>
