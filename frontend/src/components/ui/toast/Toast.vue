<script setup lang="ts">
import {
  ToastAction,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastRoot,
  ToastTitle,
  ToastViewport,
} from "reka-ui";
import { cn } from "@/lib/utils";
import type { ToastVariant } from "./useToast";
import { useToast } from "./useToast";

const { toasts } = useToast();

const variantClasses: Record<ToastVariant, string> = {
  default: "border bg-background text-foreground",
  destructive:
    "destructive group border-destructive bg-destructive text-destructive-foreground",
  success:
    "border border-green-500 bg-green-50 text-green-900 dark:bg-green-950 dark:text-green-100",
};
</script>

<template>
  <Teleport to="body">
    <ToastProvider
      v-for="toast in toasts"
      :key="toast.id"
      :duration="toast.duration ?? 5000"
      v-bind="toast"
      @update:open="
        (open: boolean) => {
          toast.onOpenChange?.(open);
        }
      "
    >
      <ToastRoot
        :class="
          cn(
            'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--reka-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--reka-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full',
            variantClasses[toast.variant ?? 'default'],
          )
        "
      >
        <div class="grid gap-1">
          <ToastTitle v-if="toast.title" class="text-sm font-semibold">
            {{ toast.title }}
          </ToastTitle>
          <ToastDescription
            v-if="toast.description"
            :class="
              cn(
                'text-sm opacity-90',
                toast.variant === 'destructive' && 'text-destructive-foreground',
              )
            "
          >
            {{ toast.description }}
          </ToastDescription>
        </div>
        <div class="flex items-center gap-2">
          <ToastAction
            v-if="toast.action"
            as-child
            :alt-text="toast.action.label"
            @click="toast.action.onClick"
          >
            <button
              class="inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:border-muted/40 group-[.destructive]:hover:border-destructive/30 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive"
            >
              {{ toast.action.label }}
            </button>
          </ToastAction>
          <ToastClose
            class="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100 group-[.destructive]:text-red-300 group-[.destructive]:hover:text-red-50 group-[.destructive]:focus:ring-red-400 group-[.destructive]:focus:ring-offset-red-600"
          />
        </div>
      </ToastRoot>
    </ToastProvider>
  </Teleport>

  <ToastViewport
    class="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse gap-2 p-4 sm:max-w-[420px]"
  />
</template>
