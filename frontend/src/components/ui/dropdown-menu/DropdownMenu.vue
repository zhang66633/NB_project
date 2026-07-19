<script setup lang="ts">
import { DropdownMenuRoot, type DropdownMenuRootProps } from "reka-ui";

export interface DropdownMenuProps {
  open?: DropdownMenuRootProps["defaultOpen"];
  onOpenChange?: (open: boolean) => void;
  dir?: DropdownMenuRootProps["dir"];
  modal?: DropdownMenuRootProps["modal"];
}

const props = defineProps<DropdownMenuProps>();

const emit = defineEmits<{
  "update:open": [value: boolean];
}>();

// Using direct v-model binding through the template
</script>

<template>
  <DropdownMenuRoot
    :open="props.open"
    :dir="props.dir"
    :modal="props.modal"
    v-bind="$attrs"
    @update:open="
      (val: boolean) => {
        props.onOpenChange?.(val);
        emit('update:open', val);
      }
    "
  >
    <slot />
  </DropdownMenuRoot>
</template>
