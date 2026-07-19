<script setup lang="ts">
import { StepperDescription, type StepperDescriptionProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperDescriptionProps & { class?: string }>();
</script>

<template>
  <StepperDescription
    :class="cn('text-xs text-muted-foreground', props.class)"
    v-bind="$attrs"
  >
    <slot />
  </StepperDescription>
</template>
