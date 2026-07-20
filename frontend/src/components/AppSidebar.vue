<template>
  <aside class="flex flex-col border-r bg-background h-screen sticky top-0 w-64 shrink-0">
    <!-- 品牌:衬线首字母方框 + 衬线 wordmark,无彩色块 -->
    <div class="flex h-14 items-center gap-2.5 border-b px-5 shrink-0">
      <div class="flex h-7 w-7 items-center justify-center border border-border rounded-sm">
        <span class="font-display text-sm font-medium leading-none">M</span>
      </div>
      <span class="font-display text-sm font-medium tracking-tight">{{ APP_NAME }}</span>
    </div>

    <!-- 导航:章节式 §序号 + 文字,当前项左竖线高亮(无图标、无填充背景) -->
    <nav class="flex-1 py-6 overflow-y-auto">
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
    <div class="border-t px-3 py-3">
      <VersionSwitcher />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import { APP_NAME } from "@/utils/const";
import { navItems } from "@/config/navItems";
import VersionSwitcher from "@/components/VersionSwitcher.vue";

const router = useRouter();
const route = useRoute();

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
</script>
