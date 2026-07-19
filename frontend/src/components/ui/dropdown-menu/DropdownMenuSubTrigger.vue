<script setup lang="ts">
import { DropdownMenuSubTrigger, type DropdownMenuSubTriggerProps } from "reka-ui";
import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-vue-next";

const props = defineProps<DropdownMenuSubTriggerProps & { inset?: boolean; class?: string }>();
</script>

<template>
  <DropdownMenuSubTrigger
    :class="
      cn(
        'flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent data-[state=open]:bg-accent',
        props.inset && 'pl-8',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <slot />
    <ChevronRight class="ml-auto h-4 w-4" />
  </DropdownMenuSubTrigger>
</template>
