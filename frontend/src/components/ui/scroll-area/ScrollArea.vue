<script lang="ts">
import { defineComponent, h } from 'vue'
import {
  ScrollAreaRoot,
  ScrollAreaViewport,
  ScrollAreaScrollbar,
  ScrollAreaThumb,
  ScrollAreaCorner,
  type ScrollAreaRootProps,
  type ScrollAreaScrollbarProps,
  type ScrollAreaThumbProps,
  type ScrollAreaViewportProps,
} from 'reka-ui'
import { cn } from '@/lib/utils'

export const ScrollBar = defineComponent({
  props: {
    orientation: { type: String as () => 'horizontal' | 'vertical' | undefined, default: 'vertical' },
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props) {
    return () => {
      const isHorizontal = props.orientation === 'horizontal'
      return h(
        ScrollAreaScrollbar,
        {
          orientation: props.orientation,
          class: cn(
            'flex touch-none select-none transition-colors',
            isHorizontal
              ? 'h-2.5 flex-col border-t border-t-transparent p-[1px]'
              : 'h-full w-2.5 border-l border-l-transparent p-[1px]',
            props.class,
          ),
        },
        {
          default: () =>
            h(ScrollAreaThumb, {
              class: 'relative flex-1 rounded-full bg-border',
            }),
        },
      )
    }
  },
})
</script>

<script setup lang="ts">
import { ScrollAreaRoot, ScrollAreaViewport, ScrollAreaCorner } from 'reka-ui'
import { cn } from '@/lib/utils'
import type { ScrollAreaRootProps } from 'reka-ui'

const props = withDefaults(defineProps<ScrollAreaRootProps & { class?: string, viewportClass?: string }>(), {
  type: 'hover',
})
</script>

<template>
  <ScrollAreaRoot
    :type="type"
    :scroll-hide-delay="scrollHideDelay"
    :dir="dir"
    :class="cn('relative overflow-hidden', props.class)"
  >
    <ScrollAreaViewport
      :class="cn('h-full w-full rounded-[inherit]', props.viewportClass)"
    >
      <slot />
    </ScrollAreaViewport>
    <ScrollBar />
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>
