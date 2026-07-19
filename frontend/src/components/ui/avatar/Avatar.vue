<script lang="ts">
import { type HTMLAttributes, defineComponent, h } from 'vue'
import { AvatarImage as RekaAvatarImage, AvatarFallback as RekaAvatarFallback } from 'reka-ui'
import { cn } from '@/lib/utils'

export const AvatarImage = defineComponent({
  props: {
    src: { type: String, default: undefined },
    alt: { type: String, default: undefined },
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props) {
    return () =>
      h(RekaAvatarImage, {
        src: props.src,
        alt: props.alt,
        class: cn('h-full w-full object-cover', props.class),
      })
  },
})

export const AvatarFallback = defineComponent({
  props: {
    class: { type: String as () => string | undefined, default: undefined },
    delayMs: { type: Number, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(
        RekaAvatarFallback,
        {
          delayMs: props.delayMs,
          class: cn(
            'flex h-full w-full items-center justify-center rounded-full bg-muted',
            props.class,
          ),
        },
        slots.default?.(),
      )
  },
})
</script>

<script setup lang="ts">
import { AvatarRoot, type AvatarRootProps } from 'reka-ui'
import { cn } from '@/lib/utils'

const rootProps = withDefaults(defineProps<AvatarRootProps & { class?: string }>(), {})
</script>

<template>
  <AvatarRoot
    :class="
      cn(
        'relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full',
        rootProps.class,
      )
    "
  >
    <slot />
  </AvatarRoot>
</template>
