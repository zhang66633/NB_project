<template>
  <div class="space-y-0.5">
    <TreeNode
      v-for="(item, idx) in items"
      :key="idx"
      :item="item"
      :level="level"
    >
      <template #default="{ item: node }">
        <slot name="item" :item="node" />
      </template>
    </TreeNode>
  </div>
</template>

<script setup lang="ts">
import TreeNode from "./TreeNode.vue";

export interface TreeNodeItem {
  id: string;
  label: string;
  children?: TreeNodeItem[];
  icon?: string;
  [key: string]: unknown;
}

defineProps<{
  items: TreeNodeItem[];
  level?: number;
}>();
</script>

<!-- TreeNode.vue -->
