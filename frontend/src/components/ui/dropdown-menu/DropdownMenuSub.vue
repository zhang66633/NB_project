<script setup lang="ts">
import { DropdownMenuSub, type DropdownMenuSubProps } from "reka-ui";

const props = defineProps<DropdownMenuSubProps>();
</script>

<template>
  <DropdownMenuSub v-bind="props">
    <slot />
  </DropdownMenuSub>
</template>
