<script setup lang="ts">
import { SelectScrollDownButton, type SelectScrollDownButtonProps } from "reka-ui";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-vue-next";

const props = defineProps<SelectScrollDownButtonProps & { class?: string }>();
</script>

<template>
  <SelectScrollDownButton
    :class="cn('flex cursor-default items-center justify-center py-1', props.class)"
    v-bind="$attrs"
  >
    <ChevronDown class="h-4 w-4" />
  </SelectScrollDownButton>
</template>
