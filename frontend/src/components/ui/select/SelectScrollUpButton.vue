<script setup lang="ts">
import { SelectScrollUpButton, type SelectScrollUpButtonProps } from "reka-ui";
import { cn } from "@/lib/utils";
import { ChevronUp } from "lucide-vue-next";

const props = defineProps<SelectScrollUpButtonProps & { class?: string }>();
</script>

<template>
  <SelectScrollUpButton
    :class="cn('flex cursor-default items-center justify-center py-1', props.class)"
    v-bind="$attrs"
  >
    <ChevronDown class="h-4 w-4" />
  </SelectScrollUpButton>
</template>
