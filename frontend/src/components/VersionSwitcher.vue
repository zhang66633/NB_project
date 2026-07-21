<template>
  <div class="relative" ref="containerRef">
    <button
      ref="buttonRef"
      class="flex w-full items-center gap-2 rounded-sm border border-border px-3 py-2 text-sm hover:bg-accent/50 transition-colors"
      @click="open = !open"
    >
      <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground shrink-0">· 版本</span>
      <span class="flex-1 text-left truncate font-display text-xs">{{ selected }}</span>
      <ChevronDown
        :class="['h-3.5 w-3.5 text-muted-foreground shrink-0 transition-transform', open && 'rotate-180']"
      />
    </button>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0 translate-y-1"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 translate-y-1"
    >
      <div
        v-if="open"
        class="absolute left-0 right-0 z-50 rounded-sm border border-border bg-popover p-1 shadow-sm"
        :style="{ bottom: `${buttonHeight + 4}px` }"
      >
        <button
          v-for="version in versions"
          :key="version"
          class="flex w-full items-center rounded-sm px-2 py-1.5 text-xs hover:bg-accent transition-colors"
          :class="version === selected ? 'bg-accent/60 font-medium' : 'text-muted-foreground'"
          @click="select(version)"
        >
          {{ version }}
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import { ChevronDown } from "lucide-vue-next";

const versions = ["MathModelAgent v0.1", "默认工作区"];

const selected = ref(versions[0]);
const open = ref(false);
const buttonRef = ref<HTMLElement | null>(null);
const containerRef = ref<HTMLElement | null>(null);
const buttonHeight = ref(40);

const emit = defineEmits<{
  change: [version: string];
}>();

function select(version: string) {
  selected.value = version;
  open.value = false;
  emit("change", version);
}

// 点击外部关闭
onMounted(() => {
  document.addEventListener("click", (e) => {
    if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
      open.value = false;
    }
  });
});

// 计算按钮高度
watch(open, async (val) => {
  if (val) {
    await nextTick();
    if (buttonRef.value) {
      buttonHeight.value = buttonRef.value.offsetHeight;
    }
  }
});
</script>
