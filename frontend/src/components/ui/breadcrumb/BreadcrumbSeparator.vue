<script setup lang="ts">
import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-vue-next";

const props = defineProps<{ class?: string }>();
</script>

<template>
  <li
    role="presentation"
    aria-hidden="true"
    :class="cn('[&>svg]:size-3.5', props.class)"
  >
    <slot>
      <ChevronRight class="h-3.5 w-3.5" />
    </slot>
  </li>
</template>
