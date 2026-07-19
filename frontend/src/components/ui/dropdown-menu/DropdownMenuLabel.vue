<script setup lang="ts">
import { DropdownMenuLabel, type DropdownMenuLabelProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<DropdownMenuLabelProps & { inset?: boolean; class?: string }>();
</script>

<template>
  <DropdownMenuLabel
    :class="
      cn(
        'px-2 py-1.5 text-sm font-semibold',
        props.inset && 'pl-8',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
  </DropdownMenuLabel>
</template>
