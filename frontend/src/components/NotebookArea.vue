<template>
  <div class="flex flex-col h-full">
    <!-- Toolbar -->
    <div class="flex items-center gap-2 border-b px-4 py-2 bg-muted/30">
      <span class="text-sm font-medium flex-1">Notebook</span>
      <button
        class="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium hover:bg-accent transition-colors"
        title="运行全部"
        @click="emit('runAll')"
      >
        <Play class="h-3.5 w-3.5" />
        <span class="hidden sm:inline">运行全部</span>
      </button>
      <button
        class="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium hover:bg-accent transition-colors"
        title="清除输出"
        @click="emit('clearOutputs')"
      >
        <Trash2 class="h-3.5 w-3.5" />
        <span class="hidden sm:inline">清除输出</span>
      </button>
      <button
        class="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium hover:bg-accent transition-colors"
        title="下载"
        @click="emit('download')"
      >
        <Download class="h-3.5 w-3.5" />
      </button>
    </div>

    <!-- Cells -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <template v-if="cells && cells.length > 0">
        <NotebookCell
          v-for="(cell, idx) in cells"
          :key="idx"
          :cell_type="(cell.cell_type as 'code' | 'markdown' | 'raw')"
          :source="cell.source"
          :execution-count="cell.execution_count"
          :outputs="cell.outputs"
          @run="emit('runCell', idx)"
        />
      </template>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center h-full text-muted-foreground">
        <BookOpen class="h-10 w-10 mb-2 opacity-30" />
        <p class="text-sm">暂无 Notebook 内容</p>
        <p class="text-xs">智能体输出后将在此显示</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Play, Trash2, Download, BookOpen } from "lucide-vue-next";
import NotebookCell from "@/components/NotebookCell.vue";

interface NotebookCellData {
  cell_type: string;
  source?: string;
  execution_count?: number;
  outputs?: Array<Record<string, unknown>>;
}

defineProps<{
  cells?: NotebookCellData[];
}>();

const emit = defineEmits<{
  runAll: [];
  runCell: [index: number];
  clearOutputs: [];
  download: [];
}>();
</script>
