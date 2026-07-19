<script setup lang="ts">
import { Separator, type SeparatorProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<SeparatorProps & { class?: string, label?: string }>(), {
  orientation: 'horizontal',
  decorative: true,
})

const isHorizontal = props.orientation === 'horizontal'
</script>

<template>
  <Separator
    :orientation="orientation"
    :decorative="decorative"
    :class="
      cn(
        'shrink-0 bg-border',
        isHorizontal ? 'h-[1px] w-full' : 'h-full w-[1px]',
        props.class,
      )
    "
  >
    <div
      v-if="label"
      :class="
        cn(
          'text-xs text-muted-foreground',
          isHorizontal ? 'mx-2' : 'my-2',
        )
      "
    >
      {{ label }}
    </div>
  </Separator>
</template>
