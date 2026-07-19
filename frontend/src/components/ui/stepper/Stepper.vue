<script setup lang="ts">
import { StepperRoot, type StepperRootProps } from "reka-ui";
import { cn } from "@/lib/utils";

export interface StepperProps {
  modelValue?: StepperRootProps["modelValue"];
  defaultValue?: StepperRootProps["defaultValue"];
  onUpdateModelValue?: (value: number) => void;
  orientation?: StepperRootProps["orientation"];
  dir?: StepperRootProps["dir"];
  linear?: boolean;
  class?: string;
}

const props = defineProps<StepperProps>();
const emit = defineEmits<{
  "update:modelValue": [value: number];
}>();
</script>

<template>
  <StepperRoot
    :model-value="props.modelValue"
    :default-value="props.defaultValue"
    :orientation="props.orientation ?? 'horizontal'"
    :dir="props.dir"
    :linear="props.linear"
    :class="cn('flex gap-2', props.class)"
    v-bind="$attrs"
    @update:model-value="
      (val: number) => {
        props.onUpdateModelValue?.(val);
        emit('update:modelValue', val);
      }
    "
  >
    <slot />
  </StepperRoot>
</template>
