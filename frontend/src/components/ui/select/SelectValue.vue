<script setup lang="ts">
import { SelectValue, type SelectValueProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<SelectValueProps & { class?: string; placeholder?: string }>();
</script>

<template>
  <SelectValue
    :class="cn(props.class)"
    :placeholder="props.placeholder ?? 'Select an option...'"
    v-bind="$attrs"
  >
    <slot />
  </SelectValue>
</template>
