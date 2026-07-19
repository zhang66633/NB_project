<template>
  <div class="flex flex-col h-full">
    <!-- Messages scroll area -->
    <div ref="scrollRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-1">
      <!-- Empty state -->
      <div v-if="messages.length === 0 && !isRunning" class="flex flex-col items-center justify-center h-full text-center">
        <MessageSquare class="h-12 w-12 text-muted-foreground/30 mb-3" />
        <p class="text-muted-foreground text-sm">开始建模对话</p>
        <p class="text-muted-foreground text-xs mt-1">输入你的数学建模问题</p>
      </div>

      <!-- Skeleton loading -->
      <div v-if="isConnecting" class="space-y-4">
        <div v-for="i in 3" :key="i" class="flex items-start gap-3 animate-pulse">
          <div class="h-8 w-8 rounded-full bg-muted" />
          <div class="space-y-2 flex-1">
            <div class="h-3 bg-muted rounded w-1/4" />
            <div class="h-3 bg-muted rounded w-3/4" />
          </div>
        </div>
      </div>

      <!-- Messages -->
      <Bubble
        v-for="(msg, idx) in messages"
        :key="msg.id || idx"
        :message="msg"
        :is-last="idx === messages.length - 1"
      />

      <!-- Typing indicator -->
      <div v-if="isRunning" class="flex items-center gap-2 pl-3 py-2">
        <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
          <Brain class="h-4 w-4 text-blue-600" />
        </div>
        <div class="flex items-center gap-1 bg-muted rounded-xl px-4 py-3">
          <span class="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 0ms" />
          <span class="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 150ms" />
          <span class="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce" style="animation-delay: 300ms" />
        </div>
      </div>

      <div ref="bottomRef" />
    </div>

    <!-- Scroll to bottom button -->
    <Transition name="fade">
      <button
        v-if="!isAtBottom"
        class="absolute bottom-24 right-6 h-9 w-9 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:bg-primary/90 transition-colors z-10"
        @click="scrollToBottom"
      >
        <ArrowDown class="h-4 w-4" />
      </button>
    </Transition>

    <!-- Input area -->
    <div class="border-t bg-background p-4">
      <div class="flex items-end gap-2">
        <textarea
          v-model="inputText"
          class="flex min-h-10 max-h-40 w-full resize-none rounded-xl border border-input bg-background px-4 py-2.5 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          placeholder="输入消息..."
          rows="1"
          :disabled="isRunning"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          ref="textareaRef"
        />
        <button
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
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
import { MessageSquare, Brain, ArrowDown, Send, Loader2 } from "lucide-vue-next";
import { useTaskStore } from "@/stores/task";
import Bubble from "@/components/Bubble.vue";

const taskStore = useTaskStore();

const emit = defineEmits<{
  send: [text: string];
}>();

const messages = computed(() => taskStore.messages);
const isRunning = computed(() => taskStore.isRunning);
const isConnecting = computed(() =>
  taskStore.wsStatus === "connecting" || taskStore.wsStatus === "reconnecting"
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
  if (!text || isRunning.value) return;
  emit("send", text);
  inputText.value = "";
  nextTick(() => {
    const el = textareaRef.value;
    if (el) el.style.height = "auto";
  });
}

// Track scroll position
function onScroll() {
  const el = scrollRef.value;
  if (!el) return;
  const threshold = 100;
  isAtBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
}

// Auto-scroll on new messages
watch(
  () => messages.value.length,
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
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
