<template>
  <aside class="flex flex-col border-r bg-background h-screen sticky top-0 w-64 shrink-0">
    <!-- 品牌 -->
    <div class="flex h-14 items-center justify-between border-b px-5 shrink-0">
      <div class="flex items-center gap-2.5">
        <div class="flex h-7 w-7 items-center justify-center border border-border rounded-sm">
          <span class="font-display text-sm font-medium leading-none">M</span>
        </div>
        <span class="font-display text-sm font-medium tracking-tight">{{ APP_NAME }}</span>
      </div>
      <button
        class="flex h-7 w-7 items-center justify-center rounded-sm hover:bg-accent transition-colors"
        title="新对话"
        @click="newChat"
      >
        <Plus class="h-4 w-4 text-muted-foreground" />
      </button>
    </div>

    <!-- 对话列表 -->
    <div v-if="sessionList.length > 0" class="border-b py-2 flex-1 overflow-y-auto">
      <p class="px-5 py-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground/60">最近对话</p>
      <div
        v-for="s in sessionList"
        :key="s.id"
        class="group relative flex w-full items-center gap-2 py-1.5 pr-2 pl-5 text-sm cursor-pointer transition-colors"
        :class="s.id === chatSession.activeSessionId ? 'text-foreground bg-accent/50' : 'text-muted-foreground hover:text-foreground hover:bg-accent/30'"
        @click="switchTo(s)"
      >
        <span
          class="font-mono text-[9px] w-7 shrink-0"
          :class="s.type === 'task' ? 'text-amber-600/70' : s.mode === 'teach' ? 'text-green-600/70' : 'text-blue-600/70'"
        >
          {{ s.type === 'task' ? '任务' : s.mode === 'teach' ? '教学' : '方案' }}
        </span>
        <span class="truncate flex-1 text-xs">{{ s.title }}</span>
        <button
          class="flex h-5 w-5 shrink-0 items-center justify-center rounded-sm opacity-0 group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive transition-all"
          @click.stop="removeSession(s.id)"
          title="删除对话"
        >
          <X class="h-3 w-3" />
        </button>
      </div>
    </div>

    <!-- 导航 -->
    <nav :class="sessionList.length > 0 ? 'py-3 shrink-0' : 'flex-1 py-6'">
      <button
        v-for="(item, i) in navItems"
        :key="item.path"
        class="group relative flex w-full items-center gap-3 py-2 pr-4 pl-5 text-sm transition-colors"
        :class="isActive(item.path) ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
        @click="navigate(item.path)"
      >
        <span
          v-if="isActive(item.path)"
          class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-px bg-primary"
          aria-hidden="true"
        />
        <span class="font-mono text-[10px] text-muted-foreground/70 w-5 shrink-0">§{{ i + 1 }}</span>
        <span :class="isActive(item.path) ? 'font-display font-medium' : ''">{{ item.label }}</span>
      </button>
    </nav>

    <!-- 底部版本切换 -->
    <div class="border-t px-3 py-3 shrink-0">
      <VersionSwitcher />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Plus, X } from "lucide-vue-next";
import { APP_NAME } from "@/utils/const";
import { navItems } from "@/config/navItems";
import VersionSwitcher from "@/components/VersionSwitcher.vue";
import { useChatSessionStore } from "@/stores/chatSession";

const router = useRouter();
const route = useRoute();
const chatSession = useChatSessionStore();

const sessionList = computed(() => chatSession.sortedSessions.slice(0, 20));

function isActive(path: string): boolean {
  if (path === "/") return route.path === "/";
  if (route.path.startsWith("/chat")) return path.startsWith("/chat");
  if (route.path.startsWith("/task")) return path.startsWith("/task");
  if (route.path.startsWith("/knowledge")) return path.startsWith("/knowledge");
  if (route.path.startsWith("/example")) return path.startsWith("/example");
  return false;
}

function navigate(path: string) {
  router.push(path);
}

function newChat() {
  chatSession.clearActive();
  router.push("/chat");
}

function switchTo(s: { id: string; type: string }) {
  chatSession.switchSession(s.id);
  if (s.type === "task") {
    router.push(`/task/${s.id}`);
  } else {
    router.push("/chat");
  }
}

function removeSession(id: string) {
  chatSession.deleteSession(id);
}
</script>
