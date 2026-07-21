<template>
  <div class="flex h-full flex-col bg-background">
    <!-- Header bar -->
    <header class="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
      <div class="flex items-center gap-2 min-w-0">
        <button
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border hover:bg-muted/50 transition-colors"
          @click="goBack"
        >
          <ArrowLeft class="h-4 w-4" />
        </button>
        <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground shrink-0">&sect; 归档</span>
        <span class="font-display text-sm font-medium truncate">{{ archive?.title || '未命名归档' }}</span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <span
          class="font-mono text-[10px] uppercase tracking-wider rounded-md border border-border px-2 py-0.5"
          :class="archive?.kind === 'solution' ? 'text-blue-600/70' : 'text-green-600/70'"
        >{{ archive?.kind === 'solution' ? '方案' : '教学' }}</span>
        <button
          class="flex h-8 w-8 items-center justify-center rounded-md border border-border hover:bg-muted/50 transition-colors"
          title="编辑备注"
          @click="startEditNote"
        >
          <FileEdit class="h-3.5 w-3.5" />
        </button>
        <button
          class="flex h-8 w-8 items-center justify-center rounded-md border border-border hover:bg-destructive/10 hover:border-destructive/30 transition-colors"
          title="删除归档"
          @click="deleteArchive"
        >
          <Trash2 class="h-3.5 w-3.5" />
        </button>
      </div>
    </header>

    <!-- Scrollable content -->
    <div class="flex-1 overflow-y-auto bg-grid-paper">
      <div class="mx-auto max-w-3xl px-6 sm:px-10 py-8">
        <!-- Meta info section -->
        <section class="mb-8">
          <div class="section-rule mb-5"><span class="font-mono text-[10px] uppercase tracking-wider">元数据</span></div>
          <div class="flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            <span>{{ archive?.source === 'selection' ? '选中消息' : '整个会话' }}</span>
            <span class="text-muted-foreground/40">&middot;</span>
            <span>{{ modeLabel }}</span>
            <span class="text-muted-foreground/40">&middot;</span>
            <span>{{ archive?.messages.length ?? 0 }} 条消息</span>
            <span class="text-muted-foreground/40">&middot;</span>
            <span>{{ createdAt }}</span>
          </div>

          <!-- Note block -->
          <div v-if="archive?.note" class="mt-4 rounded-md border border-border bg-background p-4">
            <div class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-2">备注</div>
            <p class="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{{ archive.note }}</p>
          </div>

          <!-- Edit note form -->
          <div v-if="isEditingNote" class="mt-4 rounded-md border border-border bg-background p-4 space-y-3">
            <div class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">编辑备注</div>
            <textarea
              v-model="noteText"
              class="w-full rounded-md border border-border bg-background px-3 py-2 text-sm leading-relaxed resize-y min-h-[80px] placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="添加备注..."
            />
            <div class="flex items-center gap-2">
              <button
                class="font-mono text-[10px] uppercase tracking-wider rounded-md border border-border px-3 py-1.5 hover:bg-muted/50 transition-colors"
                @click="saveNote"
              >保存</button>
              <button
                class="font-mono text-[10px] uppercase tracking-wider rounded-md border border-border px-3 py-1.5 text-muted-foreground hover:bg-muted/50 transition-colors"
                @click="isEditingNote = false"
              >取消</button>
            </div>
          </div>
        </section>

        <!-- Message list section -->
        <section>
          <div class="section-rule mb-5"><span class="font-mono text-[10px] uppercase tracking-wider">手稿内容</span></div>
          <div class="space-y-1">
            <Bubble
              v-for="(msg, idx) in archive?.messages ?? []"
              :key="msg.id"
              :message="msg"
              :is-last="false"
            />
          </div>
        </section>
      </div>
    </div>

    <!-- Footer -->
    <footer class="shrink-0 border-t border-border px-4 py-3 flex items-center justify-between">
      <span class="font-mono text-xs text-muted-foreground">此归档为只读手稿，内容来自归档时的对话记录。</span>
      <span class="font-mono text-[10px] text-muted-foreground/70">{{ createdAt }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, Trash2, FileEdit } from "lucide-vue-next";
import Bubble from "@/components/Bubble.vue";
import { useArchiveStore } from "@/stores/archive";

const route = useRoute();
const router = useRouter();
const archiveStore = useArchiveStore();

const archiveId = computed(() => route.params.id as string);
const archive = computed(() => archiveStore.getById(archiveId.value));

// Edit note state
const isEditingNote = ref(false);
const noteText = ref("");

const modeLabel = computed(() => {
  const labels: Record<string, string> = {
    teach: "教学模式",
    execute: "执行模式",
    chat: "自由对话",
  };
  return labels[archive.value?.mode ?? ""] || archive.value?.mode || "";
});

const createdAt = computed(() => {
  if (!archive.value?.createdAt) return "";
  return new Date(archive.value.createdAt).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
});

function startEditNote() {
  noteText.value = archive.value?.note || "";
  isEditingNote.value = true;
}

function saveNote() {
  if (archiveId.value) {
    archiveStore.updateNote(archiveId.value, noteText.value);
  }
  isEditingNote.value = false;
}

function deleteArchive() {
  if (archiveId.value && confirm("确认删除此归档？")) {
    archiveStore.deleteArchive(archiveId.value);
    router.push("/");
  }
}

function goBack() {
  router.back();
}

onMounted(() => {
  if (!archive.value) {
    router.replace("/");
  }
});
</script>