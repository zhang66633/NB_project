<script setup lang="ts">
import { StepperItem, type StepperItemProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperItemProps & { class?: string }>();
</script>

<template>
  <StepperItem
    :step="props.step"
    :disabled="props.disabled"
    :completed="props.completed"
    :class="cn('relative flex flex-col items-center gap-2', props.class)"
    v-bind="$attrs"
  >
    <slot />
  </StepperItem>
</template>
