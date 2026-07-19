<script lang="ts">
import { type HTMLAttributes, defineComponent, h } from 'vue'
import { TooltipProvider as RekaTooltipProvider, TooltipRoot, TooltipTrigger as RekaTooltipTrigger, TooltipPortal, TooltipContent as RekaTooltipContent, type TooltipProviderProps, type TooltipRootEmits, type TooltipRootProps, type TooltipTriggerProps, type TooltipContentEmits, type TooltipContentProps } from 'reka-ui'
import { cn } from '@/lib/utils'

export const TooltipProvider = defineComponent({
  props: {
    delayDuration: { type: Number, default: undefined },
    skipDelayDuration: { type: Number, default: undefined },
    disableHoverableContent: { type: Boolean, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(RekaTooltipProvider, { ...props }, slots.default?.())
  },
})

export const Tooltip = defineComponent({
  props: {
    defaultOpen: { type: Boolean, default: undefined },
    open: { type: Boolean, default: undefined },
    delayDuration: { type: Number, default: undefined },
    disableHoverableContent: { type: Boolean, default: undefined },
    disableClosingTrigger: { type: Boolean, default: undefined },
    disabled: { type: Boolean, default: undefined },
    ignoreNonKeyboardFocus: { type: Boolean, default: undefined },
  },
  emits: {
    'update:open': (_value: boolean) => true,
  },
  setup(props, { slots, emit }) {
    return () =>
      h(
        TooltipRoot,
        {
          ...props,
          onUpdateOpen: (val: boolean) => emit('update:open', val),
        },
        slots.default?.(),
      )
  },
})

export const TooltipTrigger = defineComponent({
  props: {
    asChild: { type: Boolean, default: undefined },
    class: { type: String as () => string | undefined, default: undefined },
  },
  setup(props, { slots }) {
    return () =>
      h(
        RekaTooltipTrigger,
        {
          asChild: props.asChild,
          class: props.class,
        },
        slots.default?.(),
      )
  },
})

export const TooltipContent = defineComponent({
  props: {
    side: { type: String as () => 'top' | 'right' | 'bottom' | 'left' | undefined, default: undefined },
    sideOffset: { type: Number, default: undefined },
    align: { type: String as () => 'start' | 'center' | 'end' | undefined, default: undefined },
    alignOffset: { type: Number, default: undefined },
    avoidCollisions: { type: Boolean, default: undefined },
    collisionBoundary: { type: [Object, Array], default: undefined },
    collisionPadding: { type: [Number, Object], default: undefined },
    arrowPadding: { type: Number, default: undefined },
    sticky: { type: String, default: undefined },
    hideWhenDetached: { type: Boolean, default: undefined },
    class: { type: String as () => string | undefined, default: undefined },
    forceMount: { type: Boolean, default: undefined },
    showArrow: { type: Boolean, default: false },
  },
  emits: {
    escapeKeyDown: (_event: Event) => true,
    pointerDownOutside: (_event: Event) => true,
  },
  setup(props, { slots, emit }) {
    return () =>
      h(
        TooltipPortal,
        {},
        {
          default: () =>
            h(
              RekaTooltipContent,
              {
                ...props,
                class: cn(
                  'z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
                  props.class,
                ),
                onEscapeKeyDown: (e: Event) => emit('escapeKeyDown', e),
                onPointerDownOutside: (e: Event) => emit('pointerDownOutside', e),
              },
              slots.default?.(),
            ),
        },
      )
  },
})
</script>

<script setup lang="ts">
// Main template-less component; all exports are from the regular script block.
</script>
