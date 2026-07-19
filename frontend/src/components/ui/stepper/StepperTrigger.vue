<script setup lang="ts">
import { StepperTrigger, type StepperTriggerProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperTriggerProps & { class?: string }>();
</script>

<template>
  <StepperTrigger
    :class="
      cn(
        'flex flex-col items-center gap-2 rounded-md p-2 text-sm font-medium transition-colors hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </StepperTrigger>
</template>
