<script lang="ts">
import { defineComponent, h } from 'vue'
import {
  CollapsibleRoot,
  CollapsibleTrigger,
  CollapsibleContent,
  type CollapsibleRootEmits,
  type CollapsibleRootProps,
  type CollapsibleTriggerProps,
  type CollapsibleContentEmits,
  type CollapsibleContentProps,
} from 'reka-ui'
import { cn } from '@/lib/utils'

export const CollapsibleTrigger = defineComponent({
  props: {
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(
        CollapsibleTrigger,
        {
          class: props.class,
        },
        slots.default?.(),
      )
  },
})

export const CollapsibleContent = defineComponent({
  props: {
    class: { type: String as () => string | undefined, default: undefined },
    forceMount: { type: Boolean, default: undefined },
  },
  emits: {
    escapeKeyDown: (_event: KeyboardEvent) => true,
  },
  setup(props, { slots, emit }) {
    return () =>
      h(
        CollapsibleContent,
        {
          class: cn(
            'overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down',
            props.class,
          ),
          forceMount: props.forceMount,
          onEscapeKeyDown: (e: KeyboardEvent) => emit('escapeKeyDown', e),
        },
        slots.default?.(),
      )
  },
})
</script>

<script setup lang="ts">
import { CollapsibleRoot, type CollapsibleRootEmits, type CollapsibleRootProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<CollapsibleRootProps & { class?: string }>(), {
  defaultOpen: false,
  disabled: false,
})

const emit = defineEmits<CollapsibleRootEmits>()
</script>

<template>
  <CollapsibleRoot
    v-bind="props"
    :class="props.class"
    @update:open="emit('update:open', $event)"
  >
    <slot />
  </CollapsibleRoot>
</template>
