<script setup lang="ts">
import { TabsRoot, type TabsRootProps } from "reka-ui";

export interface TabsProps<T extends string = string> {
  modelValue?: T;
  defaultValue?: T;
  onUpdateModelValue?: (value: T) => void;
  orientation?: TabsRootProps["orientation"];
  dir?: TabsRootProps["dir"];
  activationMode?: TabsRootProps["activationMode"];
}

const props = defineProps<TabsProps>();
const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>

<template>
  <TabsRoot
    :model-value="props.modelValue"
    :default-value="props.defaultValue"
    :orientation="props.orientation"
    :dir="props.dir"
    :activation-mode="props.activationMode"
    v-bind="$attrs"
    @update:model-value="
      (val: string) => {
        props.onUpdateModelValue?.(val);
        emit('update:modelValue', val);
      }
    "
  >
    <slot />
  </TabsRoot>
</template>
