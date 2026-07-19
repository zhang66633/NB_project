<script setup lang="ts">
import { cn } from "@/lib/utils";

const props = defineProps<{ class?: string }>();
</script>

<template>
  <nav :class="cn(props.class)" aria-label="Breadcrumb">
    <slot />
  </nav>
</template>
