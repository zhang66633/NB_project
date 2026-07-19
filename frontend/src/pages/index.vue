<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
              <Sigma class="h-4 w-4 text-primary-foreground" />
            </div>
            <span class="font-semibold text-sm">{{ APP_NAME }}</span>
          </div>
          <a
            :href="GITHUB_LINK"
            target="_blank"
            class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            title="查看源码"
          >
            <Github class="h-4 w-4" />
            <span class="hidden sm:inline">GitHub</span>
          </a>
        </div>
        <button
          class="inline-flex items-center gap-2 justify-center rounded-xl bg-[#24292e] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#1b1f23] hover:shadow-lg hover:shadow-black/20 transition-all ring-1 ring-white/10"
          @click="loginOpen = true"
        >
          <Github class="h-5 w-5" />
          <span>GitHub 登录</span>
        </button>
      </div>
    </header>

    <!-- Hero -->
    <section class="mx-auto max-w-4xl px-6 pt-20 pb-16 text-center">
      <h1 class="text-5xl font-bold tracking-tight sm:text-6xl">
        数学建模
        <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          多智能体
        </span>
        辅助系统
      </h1>
      <p class="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
        {{ APP_DESC }} — 基于 LangGraph 多智能体编排，支持教学模式与方案输出双模式，
        帮助您高效解决各类数学建模问题。
      </p>
    </section>

    <!-- Mode Cards -->
    <section class="mx-auto max-w-5xl px-6 pb-16">
      <div class="grid gap-6 sm:grid-cols-2">
        <!-- Teach mode -->
        <div
          class="group cursor-pointer rounded-3xl border-2 p-8 transition-all hover:border-green-300 hover:shadow-xl"
          :class="selectedMode === 'teach' ? 'border-green-500 bg-green-50/50 shadow-lg' : 'border-border bg-card'"
          @click="selectedMode = 'teach'"
        >
          <div class="flex items-start gap-5">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-green-100">
              <GraduationCap class="h-8 w-8 text-green-600" />
            </div>
            <div class="text-left flex-1">
              <h3 class="font-bold text-2xl">教学模式</h3>
              <p class="text-base text-muted-foreground mt-2 leading-relaxed">
                苏格拉底式引导提问，逐步培养建模思维。适合日常训练与备赛学习。
              </p>
            </div>
          </div>
          <div class="mt-6 flex items-center justify-between">
            <div class="flex items-center gap-2 text-base text-green-600">
              <Lightbulb class="h-5 w-5" />
              <span>引导式学习 · 思维展开 · 原理讲解</span>
            </div>
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-green-600 px-6 py-3 text-base font-semibold text-white hover:bg-green-700 transition-colors"
              @click.stop="enterChat('teach')"
            >
              开始学习
              <ArrowRight class="h-5 w-5" />
            </button>
          </div>
        </div>

        <!-- Execute mode -->
        <div
          class="group cursor-pointer rounded-3xl border-2 p-8 transition-all hover:border-blue-300 hover:shadow-xl"
          :class="selectedMode === 'execute' ? 'border-blue-500 bg-blue-50/50 shadow-lg' : 'border-border bg-card'"
          @click="selectedMode = 'execute'"
        >
          <div class="flex items-start gap-5">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-blue-100">
              <FileText class="h-8 w-8 text-blue-600" />
            </div>
            <div class="text-left flex-1">
              <h3 class="font-bold text-2xl">方案输出模式</h3>
              <p class="text-base text-muted-foreground mt-2 leading-relaxed">
                接收问题，结构化输出完整建模方案。适合实战解题与竞赛冲刺。
              </p>
            </div>
          </div>
          <div class="mt-6 flex items-center justify-between">
            <div class="flex items-center gap-2 text-base text-blue-600">
              <Zap class="h-5 w-5" />
              <span>完整方案 · 代码执行 · 论文输出</span>
            </div>
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white hover:bg-blue-700 transition-colors"
              @click.stop="enterChat('execute')"
            >
              开始建模
              <ArrowRight class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Login Sidebar Overlay -->
    <Transition name="slide">
      <div
        v-if="loginOpen"
        class="fixed inset-0 z-50 flex justify-end"
      >
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="loginOpen = false"
        />
        <div class="relative w-full max-w-md bg-background h-full shadow-2xl flex flex-col">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-lg font-semibold">登录</h2>
            <button
              class="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors"
              @click="loginOpen = false"
            >
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="flex-1 flex flex-col items-center justify-center px-8 py-12">
            <div class="flex h-20 w-20 items-center justify-center rounded-3xl bg-[#24292e] mb-8">
              <Github class="h-11 w-11 text-white" />
            </div>
            <h3 class="text-xl font-bold mb-2">使用 GitHub 登录</h3>
            <p class="text-sm text-muted-foreground text-center mb-8">
              一键授权登录，无需额外注册
            </p>
            <button
              class="flex h-14 w-full items-center justify-center gap-3 rounded-2xl bg-[#24292e] text-base font-semibold text-white hover:bg-[#1b1f23] hover:shadow-lg transition-all"
              :disabled="loggingIn"
              @click="handleGithubLogin"
            >
              <Loader2 v-if="loggingIn" class="h-6 w-6 animate-spin" />
              <Github v-else class="h-6 w-6" />
              {{ loggingIn ? '正在跳转...' : 'GitHub 账号登录' }}
            </button>
            <p class="mt-6 text-xs text-muted-foreground text-center">
              登录即表示同意服务条款和隐私政策
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  Sigma,
  Github,
  GraduationCap,
  FileText,
  Lightbulb,
  Zap,
  ArrowRight,
  X,
  Loader2,
} from "lucide-vue-next";
import { APP_NAME, APP_DESC, GITHUB_LINK } from "@/utils/const";

const router = useRouter();

const selectedMode = ref<"teach" | "execute">("teach");
const loginOpen = ref(false);
const loggingIn = ref(false);

function enterChat(mode: "teach" | "execute") {
  router.push({ path: "/chat", query: { mode } });
}

function handleGithubLogin() {
  loggingIn.value = true;
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID || "";
  if (!clientId) {
    alert("请先在 .env.development 中配置 VITE_GITHUB_CLIENT_ID");
    loggingIn.value = false;
    return;
  }
  const redirectUri = encodeURIComponent(window.location.origin + "/auth/callback");
  const scope = "read:user user:email";
  window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.3s ease;
}
.slide-enter-active > div:last-child,
.slide-leave-active > div:last-child {
  transition: transform 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}
.slide-enter-from > div:last-child {
  transform: translateX(100%);
}
.slide-leave-to > div:last-child {
  transform: translateX(100%);
}
</style>
