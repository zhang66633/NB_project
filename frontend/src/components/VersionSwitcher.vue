<template>
  <button
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
    enter-from-class="transform scale-95 opacity-0"
    enter-to-class="transform scale-100 opacity-100"
    leave-active-class="transition duration-75 ease-in"
    leave-from-class="transform scale-100 opacity-100"
    leave-to-class="transform scale-95 opacity-0"
  >
    <div
      v-if="open"
      class="absolute left-3 right-3 top-12 z-50 rounded-sm border border-border bg-popover p-1 shadow-sm"
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
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ChevronDown } from "lucide-vue-next";

const versions = ["MathModelAgent v0.1", "默认工作区"];

const selected = ref(versions[0]);
const open = ref(false);

const emit = defineEmits<{
  change: [version: string];
}>();

function select(version: string) {
  selected.value = version;
  open.value = false;
  emit("change", version);
}
</script>
