<script setup lang="ts">
import { DialogTrigger, type DialogTriggerProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<DialogTriggerProps & { class?: string }>();
</script>

<template>
  <DialogTrigger
    :as="props.as"
    :as-child="props.asChild"
    :class="cn(props.class)"
    v-bind="$attrs"
  >
    <slot />
  </DialogTrigger>
</template>
