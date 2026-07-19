<template>
  <div class="min-h-screen flex">
    <!-- Left decorative panel -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-purple-800 items-center justify-center p-12">
      <div class="max-w-md text-white">
        <div class="flex items-center gap-3 mb-8">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20">
            <Sigma class="h-7 w-7" />
          </div>
          <div>
            <h2 class="text-2xl font-bold">{{ APP_NAME }}</h2>
            <p class="text-blue-200 text-sm">数学建模多智能体辅助系统</p>
          </div>
        </div>
        <p class="text-lg text-blue-100 leading-relaxed">
          基于 LangGraph 多智能体编排技术，为您提供从问题分析到论文写作的全流程数学建模辅助。
        </p>
        <div class="mt-8 space-y-4">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <Brain class="h-4 w-4" />
            </div>
            <span class="text-blue-100">5 个专业智能体协同工作</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <MessagesSquare class="h-4 w-4" />
            </div>
            <span class="text-blue-100">教学模式 & 方案输出双模式</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <Code2 class="h-4 w-4" />
            </div>
            <span class="text-blue-100">代码生成 & 实时执行</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right login form -->
    <div class="flex flex-1 items-center justify-center px-6 py-12">
      <div class="w-full max-w-sm">
        <!-- Mobile logo -->
        <div class="flex items-center gap-2 mb-8 lg:hidden">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Sigma class="h-5 w-5 text-primary-foreground" />
          </div>
          <span class="font-semibold">{{ APP_NAME }}</span>
        </div>

        <div class="mb-8">
          <h1 class="text-2xl font-bold">欢迎回来</h1>
          <p class="text-sm text-muted-foreground mt-1">登录到你的账号继续建模</p>
        </div>

        <form class="space-y-4" @submit.prevent="handleLogin">
          <div class="space-y-1.5">
            <label class="text-sm font-medium" for="username">用户名 / 邮箱</label>
            <div class="relative">
              <User class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="name@example.com"
                class="flex h-11 w-full rounded-lg border border-input bg-background pl-10 pr-4 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                autocomplete="username"
              />
            </div>
          </div>

          <div class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium" for="password">密码</label>
              <a href="#" class="text-xs text-primary hover:underline">忘记密码?</a>
            </div>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="flex h-11 w-full rounded-lg border border-input bg-background pl-10 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                autocomplete="current-password"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                @click="showPassword = !showPassword"
              >
                <Eye v-if="!showPassword" class="h-4 w-4" />
                <EyeOff v-else class="h-4 w-4" />
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <input
              id="remember"
              v-model="rememberMe"
              type="checkbox"
              class="h-4 w-4 rounded border-input text-primary focus:ring-ring"
            />
            <label for="remember" class="text-sm text-muted-foreground">记住我</label>
          </div>

          <button
            type="submit"
            class="flex h-11 w-full items-center justify-center rounded-lg bg-primary text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
            :disabled="loading || !username.trim() || !password.trim()"
          >
            <Loader2 v-if="loading" class="h-4 w-4 mr-2 animate-spin" />
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-muted-foreground">
          还没有账号？
          <a href="#" class="text-primary hover:underline font-medium">注册</a>
        </p>

        <!-- Back home link -->
        <div class="mt-8 text-center">
          <router-link
            to="/"
            class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft class="h-4 w-4" />
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  Sigma,
  Brain,
  MessagesSquare,
  Code2,
  User,
  Lock,
  Eye,
  EyeOff,
  ArrowLeft,
  Loader2,
} from "lucide-vue-next";
import { APP_NAME } from "@/utils/const";

const router = useRouter();

const username = ref("");
const password = ref("");
const rememberMe = ref(false);
const showPassword = ref(false);
const loading = ref(false);

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) return;
  loading.value = true;
  // Simulate login
  await new Promise((r) => setTimeout(r, 1000));
  loading.value = false;
  router.push("/");
}
</script>
