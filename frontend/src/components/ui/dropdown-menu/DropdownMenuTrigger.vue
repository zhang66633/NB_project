<script setup lang="ts">
import { DropdownMenuTrigger, type DropdownMenuTriggerProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<DropdownMenuTriggerProps & { class?: string }>();
</script>

<template>
  <DropdownMenuTrigger
    :as="props.as"
    :as-child="props.asChild"
    :class="cn(props.class)"
    v-bind="$attrs"
  >
    <slot />
  </DropdownMenuTrigger>
</template>
