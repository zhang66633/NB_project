<script setup lang="ts">
import { StepperTitle, type StepperTitleProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<StepperTitleProps & { class?: string }>();
</script>

<template>
  <StepperTitle
    :class="
      cn(
        'text-sm font-medium text-foreground data-[state=inactive]:text-muted-foreground',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </StepperTitle>
</template>
