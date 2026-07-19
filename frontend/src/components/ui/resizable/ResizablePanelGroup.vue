<script setup lang="ts">
import { SplitterGroup, type SplitterGroupProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<SplitterGroupProps & { class?: string }>();
</script>

<template>
  <SplitterGroup
    :class="
      cn(
        'flex h-full w-full data-[panel-group-direction=vertical]:flex-col',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </SplitterGroup>
</template>
