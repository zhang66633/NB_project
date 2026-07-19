<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps<{
  as?: string;
  href?: string;
  class?: string;
}>();

// Determine the component tag
const component = computed(() => (props.href ? "a" : props.as ?? "a"));
</script>

<template>
  <component
    :is="component"
    :href="props.href"
    :class="
      cn(
        'transition-colors hover:text-foreground',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>
