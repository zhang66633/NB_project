<template>
  <div class="relative">
    <button
      class="flex items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent transition-colors"
      @click="open = !open"
    >
      <span
        class="flex h-8 w-8 shrink-0 items-center justify-center border border-border rounded-sm"
      >
        <span class="font-display text-sm font-medium leading-none">{{ initials }}</span>
      </span>
      <div class="flex-1 min-w-0 hidden sm:block">
        <p class="text-sm font-medium truncate">{{ displayName }}</p>
        <p class="text-xs text-muted-foreground truncate">本地模式</p>
      </div>
      <ChevronUp
        :class="['h-4 w-4 text-muted-foreground transition-transform hidden sm:block', open && 'rotate-180']"
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
        class="absolute right-0 top-full mt-1 w-56 rounded-md border bg-popover p-1 shadow-lg z-50"
      >
        <div class="px-2 py-1.5">
          <label class="text-xs text-muted-foreground">昵称</label>
          <input
            v-model="nickname"
            class="mt-1 flex h-8 w-full rounded-md border border-input bg-background px-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            placeholder="游客"
            @change="saveNickname"
          />
        </div>
        <div class="my-1 h-px bg-border" />
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
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ChevronUp, Settings, Key } from "lucide-vue-next";

const STORAGE_KEY = "mma:nickname";

const props = withDefaults(defineProps<{
  username?: string;
  email?: string;
}>(), {
  username: "",
  email: "",
});

const emit = defineEmits<{
  action: [action: string];
}>();

const open = ref(false);

// 游客模式:昵称存 localStorage,默认"游客"
const stored = (() => {
  try {
    return localStorage.getItem(STORAGE_KEY) || "";
  } catch {
    return "";
  }
})();
const nickname = ref(stored);

const displayName = computed(() => nickname.value.trim() || props.username || "游客");
const initials = computed(() => {
  const name = displayName.value;
  return name ? name.charAt(0).toUpperCase() : "U";
});

function saveNickname() {
  try {
    localStorage.setItem(STORAGE_KEY, nickname.value.trim());
  } catch {
    /* 忽略 */
  }
}

function handleAction(action: string) {
  open.value = false;
  emit("action", action);
}
</script>
