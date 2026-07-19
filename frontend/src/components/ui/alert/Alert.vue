<script lang="ts">
import { defineComponent, h } from 'vue'
import { cn } from '@/lib/utils'

export interface AlertTitleProps {
  class?: string
}

export const AlertTitle = defineComponent({
  props: {
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(
        'h5',
        {
          class: cn('mb-1 font-medium leading-none tracking-tight', props.class),
        },
        slots.default?.(),
      )
  },
})

export interface AlertDescriptionProps {
  class?: string
}

export const AlertDescription = defineComponent({
  props: {
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(
        'div',
        {
          class: cn('text-sm [&_p]:leading-relaxed', props.class),
        },
        slots.default?.(),
      )
  },
})
</script>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const alertVariants = cva(
  'relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground',
  {
    variants: {
      variant: {
        default: 'bg-background text-foreground',
        destructive:
          'border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export type AlertProps = VariantProps<typeof alertVariants> & {
  class?: string
}

const props = withDefaults(defineProps<AlertProps>(), {
  variant: 'default',
})
</script>

<template>
  <div
    :class="cn(alertVariants({ variant }), props.class)"
    role="alert"
  >
    <slot />
  </div>
</template>
