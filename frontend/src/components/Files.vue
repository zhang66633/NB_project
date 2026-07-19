<template>
  <div class="space-y-2">
    <!-- File list -->
    <TransitionGroup name="file-list" tag="div" class="space-y-1">
      <div
        v-for="file in files"
        :key="file.name"
        class="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-accent/50 transition-colors group"
      >
        <FileText class="h-4 w-4 text-blue-500 shrink-0" />
        <span class="flex-1 truncate">{{ file.name }}</span>
        <span class="text-xs text-muted-foreground shrink-0">{{ formatSize(file.size) }}</span>
        <button
          class="h-6 w-6 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive transition-all"
          :disabled="uploading"
          @click="removeFile(file.name)"
        >
          <X class="h-3.5 w-3.5" />
        </button>
      </div>
    </TransitionGroup>

    <!-- Empty state -->
    <div
      v-if="files.length === 0"
      class="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 text-center"
    >
      <Upload class="h-8 w-8 text-muted-foreground/50 mb-2" />
      <p class="text-sm text-muted-foreground">暂无文件</p>
      <p class="text-xs text-muted-foreground">拖拽文件到此处或点击上传</p>
    </div>

    <!-- Upload area -->
    <div
      class="flex items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25 p-3 cursor-pointer hover:border-primary/50 hover:bg-accent/30 transition-colors"
      :class="{ 'pointer-events-none opacity-50': uploading }"
      @click="triggerUpload"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <div class="flex items-center gap-2 text-sm text-muted-foreground">
        <Upload v-if="!uploading" class="h-4 w-4" />
        <Loader2 v-else class="h-4 w-4 animate-spin" />
        <span>{{ uploading ? '上传中...' : '点击或拖拽上传文件' }}</span>
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
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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
  transform: translateY(-8px);
}
</style>
