<template>
  <div class="rounded-lg border border-border bg-card overflow-hidden">
    <button
      class="w-full flex items-center justify-between px-4 py-2.5 hover:bg-accent/40 transition-colors"
      @click="$emit('toggle')"
    >
      <div class="flex items-center gap-2">
        <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">§ 执行进度</span>
        <span class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium" :class="statusClass">
          <span class="h-1.5 w-1.5 rounded-full" :class="statusDotClass" />
          {{ statusLabel }}
        </span>
      </div>
      <ChevronDown class="h-3.5 w-3.5 text-muted-foreground transition-transform" :class="{ 'rotate-180': open }" />
    </button>
    <Transition name="collapse">
      <div v-show="open" class="px-4 pb-4 pt-1">
        <ol class="relative space-y-3">
          <li v-for="(s, idx) in steps" :key="s.id" class="relative pl-9">
            <span
              v-if="idx !== steps.length - 1"
              class="absolute left-3 top-6 h-[calc(100%-0.5rem)] w-px"
              :class="s.status === 'done' ? 'bg-primary/60' : 'bg-border'"
            />
            <span
              class="absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full border-2 text-[10px] font-semibold"
              :class="nodeClass(s.status)"
            >
              <Loader2 v-if="s.status === 'active'" class="h-3 w-3 animate-spin" />
              <Check v-else-if="s.status === 'done'" class="h-3 w-3" />
              <span v-else>{{ idx + 1 }}</span>
            </span>
            <div class="flex flex-col">
              <span class="text-sm font-medium" :class="s.status === 'wait' ? 'text-muted-foreground' : 'text-foreground'">
                {{ s.label }}
              </span>
              <span class="text-xs text-muted-foreground">{{ s.description }}</span>
            </div>
          </li>
        </ol>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { ChevronDown, Check, Loader2 } from "lucide-vue-next";

export interface ProgressStep {
  id: string;
  label: string;
  description: string;
  status: "wait" | "active" | "done";
}

const props = withDefaults(
  defineProps<{
    steps: ProgressStep[];
    open?: boolean;
    running?: boolean;
    completed?: boolean;
    wsStatus?: string;
  }>(),
  { open: true, running: false, completed: false },
);

defineEmits<{ toggle: [] }>();

const statusLabel = computed(() => {
  if (props.completed) return "已完成";
  if (props.running) {
    const cur = props.steps.find((s) => s.status === "active");
    return cur ? `正在执行：${cur.label}` : "正在初始化";
  }
  return "空闲";
});

const statusClass = computed(() => {
  if (props.completed) return "bg-emerald-100 text-emerald-700";
  if (props.running) return "bg-amber-100 text-amber-700";
  return "bg-muted text-muted-foreground";
});

const statusDotClass = computed(() => {
  if (props.completed) return "bg-emerald-500";
  if (props.running) return "bg-amber-500 animate-pulse";
  return "bg-muted-foreground/40";
});

function nodeClass(status: ProgressStep["status"]) {
  if (status === "active") return "border-primary bg-primary text-primary-foreground";
  if (status === "done") return "border-primary bg-primary text-primary-foreground";
  return "border-border bg-background text-muted-foreground";
}
</script>

<style scoped>
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
}
.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 600px;
}
</style>