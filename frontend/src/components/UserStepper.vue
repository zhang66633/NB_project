<template>
  <div class="space-y-0.5">
    <div
      v-for="(step, idx) in steps"
      :key="step.id"
      class="flex gap-3"
    >
      <!-- Indicator column -->
      <div class="flex flex-col items-center">
        <!-- Circle -->
        <div
          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 transition-colors duration-300"
          :class="indicatorClass(step.status)"
        >
          <Check v-if="step.status === 'done'" class="h-3.5 w-3.5" />
          <Loader2 v-else-if="step.status === 'active'" class="h-3.5 w-3.5 animate-spin" />
          <X v-else-if="step.status === 'error'" class="h-3.5 w-3.5" />
          <span v-else class="text-xs font-medium">{{ idx + 1 }}</span>
        </div>
        <!-- Connector line -->
        <div
          v-if="idx < steps.length - 1"
          class="w-0.5 flex-1 min-h-4 transition-colors duration-300"
          :class="step.status === 'done' ? 'bg-primary' : 'bg-border'"
        />
      </div>

      <!-- Content -->
      <div class="pb-4 flex-1 min-w-0">
        <p
          class="text-sm font-medium transition-colors"
          :class="step.status === 'active' ? 'text-foreground' : 'text-muted-foreground'"
        >
          {{ step.label }}
        </p>
        <p
          v-if="step.description"
          class="text-xs text-muted-foreground mt-0.5"
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
      return "border-primary bg-primary text-primary-foreground";
    case "active":
      return "border-primary text-primary";
    case "error":
      return "border-destructive bg-destructive text-destructive-foreground";
    default:
      return "border-muted-foreground/30 text-muted-foreground";
  }
}
</script>
