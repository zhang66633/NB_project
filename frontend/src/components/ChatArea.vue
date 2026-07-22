<template>
  <div class="flex flex-col h-full relative">
    <div ref="scrollRef" class="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-1">
      <div v-if="messages.length === 0 && !isRunning" class="flex flex-col justify-center h-full max-w-md mx-auto px-4">
        <p class="font-display text-xl text-muted-foreground">{{ emptyText }}</p>
        <p class="text-sm text-muted-foreground/70 mt-1">{{ emptySubtext }}</p>
      </div>

      <div v-if="isConnecting" class="space-y-4">
        <div v-for="i in 3" :key="i" class="flex items-start gap-3 animate-pulse">
          <div class="h-8 w-8 rounded-sm border border-border" />
          <div class="space-y-2 flex-1">
            <div class="h-3 bg-muted rounded w-1/4" />
            <div class="h-3 bg-muted rounded w-3/4" />
          </div>
        </div>
      </div>

      <Bubble
        v-for="(msg, idx) in messages"
        :key="msg.id || idx"
        :message="msg"
        :is-last="idx === messages.length - 1"
      />

      <div v-if="isRunning" class="flex items-center gap-3 pl-1 py-2">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-sm border border-border">
          <Brain class="h-4 w-4 text-muted-foreground" />
        </div>
        <div class="flex items-center gap-1.5 rounded-md border border-border bg-background px-4 py-3">
          <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mr-2">思考中</span>
          <span class="h-1.5 w-1.5 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 0ms" />
          <span class="h-1.5 w-1.5 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 150ms" />
          <span class="h-1.5 w-1.5 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 300ms" />
        </div>
      </div>

      <div ref="bottomRef" />
    </div>

    <Transition name="fade">
      <button
        v-if="!isAtBottom"
        class="absolute bottom-24 right-6 h-9 w-9 rounded-md border border-border bg-background/80 backdrop-blur flex items-center justify-center hover:bg-accent transition-colors z-10"
        @click="scrollToBottom"
      >
        <ArrowDown class="h-4 w-4" />
      </button>
    </Transition>

    <div class="border-t border-border bg-background p-4">
      <div class="flex items-end gap-2">
        <textarea
          v-model="inputText"
          class="flex min-h-10 max-h-40 w-full resize-none rounded-md border border-border bg-background px-4 py-2.5 text-sm leading-relaxed placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          :placeholder="inputPlaceholder"
          rows="1"
          :disabled="isRunning"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          ref="textareaRef"
        />
        <button
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-foreground text-background hover:bg-foreground/90 transition-colors disabled:opacity-50"
          :disabled="!inputText.trim() || isRunning"
          @click="sendMessage"
        >
          <Send v-if="!isRunning" class="h-4 w-4" />
          <Loader2 v-else class="h-4 w-4 animate-spin" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from "vue";
import { Brain, ArrowDown, Send, Loader2 } from "lucide-vue-next";
import { useTaskStore } from "@/stores/task";
import Bubble from "@/components/Bubble.vue";
import type { Message } from "@/types/response";

const props = withDefaults(defineProps<{
  messages: Message[];
  isRunning?: boolean;
  emptyText?: string;
  emptySubtext?: string;
  inputPlaceholder?: string;
}>(), {
  isRunning: false,
  emptyText: "开始对话",
  emptySubtext: "在下方输入你的问题",
  inputPlaceholder: "输入消息...",
});

const emit = defineEmits<{
  send: [text: string];
}>();

const taskStore = useTaskStore();

const isConnecting = computed(() =>
  taskStore.wsStatus === "connecting" || taskStore.wsStatus === "reconnecting",
);

const inputText = ref("");
const scrollRef = ref<HTMLElement | null>(null);
const bottomRef = ref<HTMLElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const isAtBottom = ref(true);

function autoResize() {
  const el = textareaRef.value;
  if (!el) return;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 160) + "px";
}

function scrollToBottom() {
  bottomRef.value?.scrollIntoView({ behavior: "smooth" });
}

function sendMessage() {
  const text = inputText.value.trim();
  if (!text || props.isRunning) return;
  emit("send", text);
  inputText.value = "";
  nextTick(() => {
    const el = textareaRef.value;
    if (el) el.style.height = "auto";
  });
}

function onScroll() {
  const el = scrollRef.value;
  if (!el) return;
  const threshold = 100;
  isAtBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
}

watch(
  () => props.messages.length,
  () => {
    if (isAtBottom.value) {
      nextTick(() => scrollToBottom());
    }
  },
);

onMounted(() => {
  scrollRef.value?.addEventListener("scroll", onScroll);
});

onUnmounted(() => {
  scrollRef.value?.removeEventListener("scroll", onScroll);
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
