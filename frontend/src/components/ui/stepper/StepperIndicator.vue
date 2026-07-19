<script setup lang="ts">
import { StepperIndicator, type StepperIndicatorProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperIndicatorProps & { class?: string }>();
</script>

<template>
  <StepperIndicator
    :class="
      cn(
        'relative flex h-10 w-10 items-center justify-center rounded-full border-2 border-muted-foreground/25 text-center text-sm font-medium text-muted-foreground transition-colors data-[state=completed]:border-primary data-[state=completed]:bg-primary data-[state=completed]:text-primary-foreground data-[state=active]:border-primary data-[state=active]:text-primary',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </StepperIndicator>
</template>
