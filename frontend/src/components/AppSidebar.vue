<template>
  <aside
    :class="[
      'flex flex-col border-r bg-background transition-all duration-300',
      'h-screen sticky top-0',
      collapsed ? 'w-16' : 'w-64',
    ]"
  >
    <!-- Header -->
    <div class="flex h-14 items-center border-b px-3">
      <div v-if="!collapsed" class="flex items-center gap-2 flex-1 min-w-0">
        <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
          <Sigma class="h-4 w-4 text-primary-foreground" />
        </div>
        <span class="font-semibold text-sm truncate">{{ APP_NAME }}</span>
      </div>
      <div v-else class="flex w-full justify-center">
        <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
          <Sigma class="h-4 w-4 text-primary-foreground" />
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-1 p-2 overflow-y-auto">
      <button
        v-for="item in navItems"
        :key="item.path"
        class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
        :class="isActive(item.path)
          ? 'bg-accent text-accent-foreground font-medium'
          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
        :title="collapsed ? item.label : ''"
        @click="navigate(item.path)"
      >
        <component :is="item.icon" class="h-4 w-4 shrink-0" />
        <span v-if="!collapsed">{{ item.label }}</span>
      </button>
    </nav>

    <!-- Version Switcher -->
    <div v-if="!collapsed" class="relative px-2 pb-2">
      <VersionSwitcher />
    </div>

    <!-- User -->
    <div class="border-t p-2">
      <NavUser
        v-if="!collapsed"
        username="数学建模者"
        email="user@mathmodel.cn"
        @action="handleUserAction"
      />
      <div v-else class="flex justify-center">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-medium text-sm cursor-pointer"
          @click="router.push('/login')"
        >
          U
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import {
  Home,
  MessageSquare,
  FolderOpen,
  Library,
  BookOpen,
  Sigma,
} from "lucide-vue-next";
import { APP_NAME } from "@/utils/const";
import NavUser from "@/components/NavUser.vue";
import VersionSwitcher from "@/components/VersionSwitcher.vue";

withDefaults(defineProps<{
  collapsed?: boolean;
}>(), {
  collapsed: false,
});

const router = useRouter();
const route = useRoute();

const navItems = [
  { label: "首页", path: "/", icon: Home },
  { label: "对话", path: "/chat", icon: MessageSquare },
  { label: "任务", path: "/task/0", icon: FolderOpen },
  { label: "知识库", path: "/knowledge", icon: Library },
  { label: "例题", path: "/example/1", icon: BookOpen },
];

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

function handleUserAction(action: string) {
  if (action === "logout") {
    router.push("/");
  }
}
</script>
