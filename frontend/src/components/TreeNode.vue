<template>
  <div>
    <div
      class="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm cursor-pointer hover:bg-accent transition-colors"
      :style="{ paddingLeft: `${level * 16 + 8}px` }"
      @click="toggle"
    >
      <!-- Toggle icon -->
      <button
        v-if="hasChildren"
        class="flex h-4 w-4 items-center justify-center shrink-0 text-muted-foreground"
      >
        <ChevronRight
          :class="['h-3.5 w-3.5 transition-transform', expanded && 'rotate-90']"
        />
      </button>
      <div v-else class="w-4 shrink-0" />

      <!-- Node icon -->
      <component
        v-if="item.icon"
        :is="iconComponent"
        class="h-4 w-4 text-muted-foreground shrink-0"
      />

      <!-- Node content -->
      <span class="flex-1 truncate">
        <slot :item="item">{{ item.label }}</slot>
      </span>
    </div>

    <!-- Children -->
    <div v-if="hasChildren && expanded">
      <TreeNode
        v-for="(child, idx) in item.children"
        :key="idx"
        :item="child"
        :level="level + 1"
      >
        <template #default="{ item: childItem }">
          <slot name="item" :item="childItem" />
        </template>
      </TreeNode>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, type Component } from "vue";
import { ChevronRight, Folder, FileText } from "lucide-vue-next";
import type { TreeNodeItem } from "./Tree.vue";

const props = defineProps<{
  item: TreeNodeItem;
  level?: number;
}>();

const expanded = ref(false);

const hasChildren = computed(
  () => props.item.children && props.item.children.length > 0
);

const iconComponent = computed<Component>(() => {
  if (props.item.icon === "folder") return Folder;
  if (props.item.icon === "file") return FileText;
  return Folder;
});

function toggle() {
  if (hasChildren.value) {
    expanded.value = !expanded.value;
  }
}
</script>
