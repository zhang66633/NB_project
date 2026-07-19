<script setup lang="ts">
import { DialogClose, type DialogCloseProps } from "reka-ui";
import { cn } from "@/lib/utils";

const props = defineProps<DialogCloseProps & { class?: string }>();
</script>

<template>
  <DialogClose
    :class="cn(props.class)"
    v-bind="$attrs"
  >
    <slot />
  </DialogClose>
</template>
