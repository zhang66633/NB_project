<script setup lang="ts">
import { DialogDescription, type DialogDescriptionProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<DialogDescriptionProps & { class?: string }>();
</script>

<template>
  <DialogDescription
    :class="cn('text-sm text-muted-foreground', props.class)"
    v-bind="$attrs"
  >
    <slot />
  </DialogDescription>
</template>
