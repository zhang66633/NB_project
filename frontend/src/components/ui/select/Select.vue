<script setup lang="ts">
import { SelectRoot, type SelectRootProps } from "reka-ui";

export interface SelectProps<T = string> {
  modelValue?: T;
  defaultValue?: T;
  onUpdateModelValue?: (value: T) => void;
  dir?: SelectRootProps["dir"];
  disabled?: boolean;
  name?: string;
  required?: boolean;
  multiple?: boolean;
}

const props = defineProps<SelectProps>();
const emit = defineEmits<{
  "update:modelValue": [value: unknown];
}>();

// Using pass-through to reka-ui SelectRoot
</script>

<template>
  <SelectRoot
    :model-value="props.modelValue"
    :default-value="props.defaultValue"
    :dir="props.dir"
    :disabled="props.disabled"
    :name="props.name"
    :required="props.required"
    :multiple="props.multiple"
    v-bind="$attrs"
    @update:model-value="
      (val: unknown) => {
        props.onUpdateModelValue?.(val);
        emit('update:modelValue', val);
      }
    "
  >
    <slot />
  </SelectRoot>
</template>
