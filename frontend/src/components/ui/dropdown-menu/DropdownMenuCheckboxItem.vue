<script setup lang="ts">
import {
  DropdownMenuCheckboxItem,
  DropdownMenuItemIndicator,
  type DropdownMenuCheckboxItemProps,
} from "reka-ui";
import { cn } from "@/lib/utils";
import { Check } from "lucide-vue-next";

const props = defineProps<DropdownMenuCheckboxItemProps & { class?: string }>();
</script>

<template>
  <DropdownMenuCheckboxItem
    :class="
      cn(
        'relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        props.class,
      )
    "
    v-bind="$attrs"
  >
    <span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <DropdownMenuItemIndicator>
        <Check class="h-4 w-4" />
      </DropdownMenuItemIndicator>
    </span>
    <slot />
  </DropdownMenuCheckboxItem>
</template>
