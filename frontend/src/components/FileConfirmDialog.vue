<template>
  <div class="space-y-4">
    <div class="text-center">
      <h3 class="text-lg font-semibold">确认提交</h3>
      <p class="text-sm text-muted-foreground mt-1">请确认以下信息后提交建模任务</p>
    </div>

    <!-- Problem preview -->
    <div class="space-y-1">
      <label class="text-xs font-medium text-muted-foreground">问题描述</label>
      <div class="rounded-lg border bg-muted/30 p-3 text-sm max-h-32 overflow-y-auto whitespace-pre-wrap">
        {{ problem || '(未输入问题)' }}
      </div>
    </div>

    <!-- Mode -->
    <div class="space-y-1">
      <label class="text-xs font-medium text-muted-foreground">执行模式</label>
      <div class="flex items-center gap-2">
        <span
          class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
          :class="mode === 'execute' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'"
        >
          {{ mode === 'execute' ? '方案输出模式' : '教学模式' }}
        </span>
      </div>
    </div>

    <!-- Files -->
    <div class="space-y-1" v-if="files && files.length > 0">
      <label class="text-xs font-medium text-muted-foreground">附件 ({{ files.length }} 个)</label>
      <div class="space-y-1">
        <div
          v-for="file in files"
          :key="file.name"
          class="flex items-center gap-2 rounded border px-2 py-1 text-xs"
        >
          <FileText class="h-3 w-3 text-muted-foreground" />
          <span class="flex-1 truncate">{{ file.name }}</span>
          <span class="text-muted-foreground">{{ formatSize(file.size) }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-2 pt-2">
      <button
        class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
        @click="$emit('cancel')"
      >
        取消
      </button>
      <button
        class="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
        :disabled="!problem || submitting"
        @click="$emit('confirm')"
      >
        <Loader2 v-if="submitting" class="h-4 w-4 mr-1.5 animate-spin" />
        {{ submitting ? '提交中...' : '确认提交' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileText, Loader2 } from "lucide-vue-next";

interface FileItem {
  name: string;
  size: number;
}

defineProps<{
  problem?: string;
  mode?: string;
  files?: FileItem[];
  submitting?: boolean;
}>();

defineEmits<{
  confirm: [];
  cancel: [];
}>();

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
</script>
