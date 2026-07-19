<template>
  <div class="relative">
    <button
      class="flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left text-sm hover:bg-accent transition-colors"
      @click="open = !open"
    >
      <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary font-medium text-sm">
        {{ initials }}
      </span>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium truncate">{{ username }}</p>
        <p class="text-xs text-muted-foreground truncate">{{ email }}</p>
      </div>
      <ChevronUp
        :class="['h-4 w-4 text-muted-foreground transition-transform', open && 'rotate-180']"
      />
    </button>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="open"
        class="absolute bottom-full left-0 mb-1 w-full rounded-lg border bg-popover p-1 shadow-lg z-50"
      >
        <button
          class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-accent transition-colors"
          @click="handleAction('settings')"
        >
          <Settings class="h-4 w-4" />
          <span>设置</span>
        </button>
        <button
          class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-accent transition-colors"
          @click="handleAction('apikeys')"
        >
          <Key class="h-4 w-4" />
          <span>API Keys</span>
        </button>
        <div class="my-1 h-px bg-border" />
        <button
          class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-destructive hover:bg-destructive/10 transition-colors"
          @click="handleAction('logout')"
        >
          <LogOut class="h-4 w-4" />
          <span>退出登录</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ChevronUp, Settings, Key, LogOut } from "lucide-vue-next";

defineProps<{
  username?: string;
  email?: string;
}>();

const emit = defineEmits<{
  action: [action: string];
}>();

const open = ref(false);

const initials = "U";

function handleAction(action: string) {
  open.value = false;
  emit("action", action);
}
</script>
