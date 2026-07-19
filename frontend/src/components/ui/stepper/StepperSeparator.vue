<script setup lang="ts">
import { StepperSeparator, type StepperSeparatorProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperSeparatorProps & { class?: string }>();
</script>

<template>
  <StepperSeparator
    :class="
      cn(
        'h-0.5 flex-1 bg-muted data-[state=completed]:bg-primary',
        props.class,
      )
    "
    v-bind="$attrs"
  />
</template>
