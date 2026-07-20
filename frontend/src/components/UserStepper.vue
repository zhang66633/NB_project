<template>
  <div class="space-y-0.5">
    <div
      v-for="(step, idx) in steps"
      :key="step.id"
      class="flex gap-3"
    >
      <!-- 指示器列:方框(非圆形),细线 -->
      <div class="flex flex-col items-center">
        <div
          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm border transition-colors duration-300"
          :class="indicatorClass(step.status)"
        >
          <Check v-if="step.status === 'done'" class="h-3.5 w-3.5" />
          <Loader2 v-else-if="step.status === 'active'" class="h-3.5 w-3.5 animate-spin" />
          <X v-else-if="step.status === 'error'" class="h-3.5 w-3.5" />
          <span v-else class="font-mono text-[10px] text-muted-foreground">{{ idx + 1 }}</span>
        </div>
        <!-- 连接线:暖橙表完成,细灰表未完成 -->
        <div
          v-if="idx < steps.length - 1"
          class="w-px flex-1 min-h-4 transition-colors duration-300"
          :class="step.status === 'done' ? 'bg-primary' : 'bg-border'"
        />
      </div>

      <!-- 内容:衬线标签 + 等宽序号 -->
      <div class="pb-4 flex-1 min-w-0">
        <div class="flex items-baseline gap-2">
          <span class="font-mono text-[10px] text-muted-foreground/60 shrink-0">{{ idx + 1 }}.</span>
          <p
            class="text-sm transition-colors"
            :class="step.status === 'active' ? 'text-foreground font-display font-medium' : 'text-muted-foreground'"
          >
            {{ step.label }}
          </p>
        </div>
        <p
          v-if="step.description"
          class="text-xs text-muted-foreground/80 mt-0.5 pl-5"
        >
          {{ step.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check, Loader2, X } from "lucide-vue-next";

interface Step {
  id: string;
  label: string;
  description?: string;
  status: "wait" | "active" | "done" | "error";
}

defineProps<{
  steps: Step[];
}>();

function indicatorClass(status: string): string {
  switch (status) {
    case "done":
      return "border-primary bg-primary/10 text-primary";
    case "active":
      return "border-primary text-primary";
    case "error":
      return "border-destructive bg-destructive/10 text-destructive";
    default:
      return "border-border text-muted-foreground";
  }
}
</script>
