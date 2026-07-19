import { ref } from "vue";

export type ToastVariant = "default" | "destructive" | "success";

export interface ToastOptions {
  title?: string;
  description?: string;
  variant?: ToastVariant;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface Toast extends ToastOptions {
  id: string;
  onOpenChange?: (open: boolean) => void;
}

const TOAST_LIMIT = 5;
const TOAST_REMOVE_DELAY = 1000000;

const toasts = ref<Toast[]>([]);
const listeners: Array<() => void> = [];

let count = 0;

function genId(): string {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return `toast_${count.toString()}`;
}

function notifyListeners() {
  for (const listener of listeners) {
    listener();
  }
}

function addToast(options: ToastOptions): Toast {
  const id = genId();
  const toast: Toast = {
    ...options,
    id,
    onOpenChange: (open: boolean) => {
      if (!open) {
        removeToast(id);
      }
    },
  };

  toasts.value = [toast, ...toasts.value].slice(0, TOAST_LIMIT);
  notifyListeners();

  return toast;
}

function updateToast(id: string, options: Partial<ToastOptions>): void {
  toasts.value = toasts.value.map((t) =>
    t.id === id ? { ...t, ...options } : t,
  );
  notifyListeners();
}

function removeToast(id: string): void {
  toasts.value = toasts.value.filter((t) => t.id !== id);
  notifyListeners();
}

function dismiss(): void {
  toasts.value = [];
  notifyListeners();
}

export function useToast() {
  return {
    toasts,
    toast: addToast,
    update: updateToast,
    dismiss,
    remove: removeToast,
    onUpdate: (callback: () => void) => {
      listeners.push(callback);
      return () => {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      };
    },
  };
}
