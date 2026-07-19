<script setup lang="ts">
import { SplitterPanel, type SplitterPanelProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<SplitterPanelProps & { class?: string }>();
</script>

<template>
  <SplitterPanel :class="cn('overflow-hidden', props.class)" v-bind="$attrs">
    <slot />
  </SplitterPanel>
</template>
