<script setup lang="ts">
import {
  DropdownMenuRadioItem,
  DropdownMenuItemIndicator,
  type DropdownMenuRadioItemProps,
} from "reka-ui";
import { cn } from "@/lib/utils";
import { Circle } from "lucide-vue-next";

const props = defineProps<DropdownMenuRadioItemProps & { class?: string }>();
</script>

<template>
  <DropdownMenuRadioItem
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
        <Circle class="h-2 w-2 fill-current" />
      </DropdownMenuItemIndicator>
    </span>
    <slot />
  </DropdownMenuRadioItem>
</template>
