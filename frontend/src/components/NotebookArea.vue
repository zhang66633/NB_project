<template>
  <div class="flex flex-col h-full">
    <!-- Toolbar:等宽小标 + 细线按钮 -->
    <div class="flex items-center gap-1 border-b px-3 py-2 shrink-0">
      <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground flex-1">Notebook</span>
      <button
        class="flex items-center gap-1 rounded-sm px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="运行全部"
        @click="emit('runAll')"
      >
        <Play class="h-3 w-3" />
        <span class="hidden sm:inline">运行</span>
      </button>
      <button
        class="flex items-center gap-1 rounded-sm px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="清除输出"
        @click="emit('clearOutputs')"
      >
        <Trash2 class="h-3 w-3" />
        <span class="hidden sm:inline">清除</span>
      </button>
      <button
        class="flex items-center gap-1 rounded-sm px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="下载"
        @click="emit('download')"
      >
        <Download class="h-3 w-3" />
      </button>
    </div>

    <!-- Cells -->
    <div class="flex-1 overflow-y-auto p-3 space-y-3">
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

      <!-- Empty:左对齐文字,无彩色图标 -->
      <div v-else class="flex flex-col justify-center h-full px-2">
        <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/60">· 笔记</p>
        <p class="font-display text-sm text-muted-foreground mt-1">暂无 Notebook 内容</p>
        <p class="text-xs text-muted-foreground/70 mt-0.5">智能体输出后将在此显示</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Play, Trash2, Download } from "lucide-vue-next";
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
