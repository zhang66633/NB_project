<template>
  <div class="space-y-2">
    <!-- File list:细线列表,等宽大小 -->
    <TransitionGroup name="file-list" tag="div" class="space-y-1">
      <div
        v-for="file in files"
        :key="file.name"
        class="group flex items-center gap-2 rounded-sm border border-border bg-background px-3 py-2 text-sm hover:border-primary/40 transition-colors"
      >
        <FileText class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        <span class="flex-1 truncate">{{ file.name }}</span>
        <span class="font-mono text-[10px] text-muted-foreground/70 shrink-0 tabular-nums">{{ formatSize(file.size) }}</span>
        <button
          class="flex h-5 w-5 items-center justify-center rounded-sm opacity-0 group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive transition-all"
          :disabled="uploading"
          @click="removeFile(file.name)"
        >
          <X class="h-3 w-3" />
        </button>
      </div>
    </TransitionGroup>

    <!-- Empty:左对齐文字,无彩色图标 -->
    <div
      v-if="files.length === 0"
      class="rounded-sm border border-dashed border-border px-3 py-4"
    >
      <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/60">· 文件</p>
      <p class="text-sm text-muted-foreground mt-1">暂无文件</p>
      <p class="text-xs text-muted-foreground/70 mt-0.5">拖拽或点击下方上传</p>
    </div>

    <!-- Upload area:细线方框,等宽提示 -->
    <div
      class="flex items-center justify-center rounded-sm border border-dashed border-border px-3 py-2.5 cursor-pointer hover:border-primary/50 hover:bg-accent/30 transition-colors"
      :class="{ 'pointer-events-none opacity-50': uploading }"
      @click="triggerUpload"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <div class="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
        <Loader2 v-if="uploading" class="h-3 w-3 animate-spin" />
        <Upload v-else class="h-3 w-3" />
        <span>{{ uploading ? '上传中' : '上传文件' }}</span>
      </div>
    </div>

    <input
      ref="fileInputRef"
      type="file"
      class="hidden"
      multiple
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { FileText, X, Upload, Loader2 } from "lucide-vue-next";

interface FileItem {
  name: string;
  size: number;
}

const props = defineProps<{
  files?: FileItem[];
  uploading?: boolean;
}>();

const emit = defineEmits<{
  upload: [files: File[]];
  remove: [fileName: string];
}>();

const fileInputRef = ref<HTMLInputElement | null>(null);

function triggerUpload() {
  fileInputRef.value?.click();
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    emit("upload", Array.from(target.files));
    target.value = "";
  }
}

function handleDrop(event: DragEvent) {
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    emit("upload", Array.from(event.dataTransfer.files));
  }
}

function removeFile(name: string) {
  emit("remove", name);
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}
</script>

<style scoped>
.file-list-enter-active,
.file-list-leave-active {
  transition: all 0.2s ease;
}
.file-list-enter-from,
.file-list-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
