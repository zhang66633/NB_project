<template>
  <div class="min-h-screen flex">
    <!-- Left decorative panel -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-950 items-center justify-center p-12">
      <div class="max-w-md text-white">
        <div class="flex items-center gap-3 mb-8">
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
            <Github class="h-7 w-7" />
          </div>
          <div>
            <h2 class="text-2xl font-bold">{{ APP_NAME }}</h2>
            <p class="text-gray-400 text-sm">数学建模多智能体辅助系统</p>
          </div>
        </div>
        <p class="text-lg text-gray-300 leading-relaxed">
          使用 GitHub 账号一键登录，无需额外注册。你的建模数据将安全地关联到你的 GitHub 账号。
        </p>
        <div class="mt-8 space-y-4">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <Shield class="h-4 w-4" />
            </div>
            <span class="text-gray-300">GitHub OAuth 安全授权</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <Zap class="h-4 w-4" />
            </div>
            <span class="text-gray-300">一键登录，无需密码</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
              <Users class="h-4 w-4" />
            </div>
            <span class="text-gray-300">开源社区驱动</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right login panel -->
    <div class="flex flex-1 items-center justify-center px-6 py-12 bg-background">
      <div class="w-full max-w-sm">
        <!-- Mobile logo -->
        <div class="flex items-center justify-center gap-2 mb-8 lg:hidden">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Sigma class="h-5 w-5 text-primary-foreground" />
          </div>
          <span class="font-semibold">{{ APP_NAME }}</span>
        </div>

        <!-- GitHub icon -->
        <div class="flex justify-center mb-6">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#24292e]">
            <Github class="h-9 w-9 text-white" />
          </div>
        </div>

        <div class="text-center mb-8">
          <h1 class="text-2xl font-bold">登录 MathModelAgent</h1>
          <p class="text-sm text-muted-foreground mt-2">
            使用 GitHub 账号授权登录，即刻开始建模
          </p>
        </div>

        <!-- GitHub login button -->
        <button
          class="flex h-12 w-full items-center justify-center gap-3 rounded-xl bg-[#24292e] text-sm font-medium text-white hover:bg-[#1b1f23] transition-colors disabled:opacity-50"
          :disabled="loading"
          @click="handleGithubLogin"
        >
          <Loader2 v-if="loading" class="h-5 w-5 animate-spin" />
          <Github v-else class="h-5 w-5" />
          {{ loading ? '正在跳转 GitHub 授权...' : '使用 GitHub 账号登录' }}
        </button>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t" />
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-background px-2 text-muted-foreground">登录后你可以</span>
          </div>
        </div>

        <!-- Feature list -->
        <div class="space-y-3">
          <div class="flex items-center gap-3 rounded-lg border p-3">
            <MessageSquare class="h-5 w-5 text-primary shrink-0" />
            <div>
              <p class="text-sm font-medium">多智能体对话</p>
              <p class="text-xs text-muted-foreground">5 个专业智能体协同解决建模问题</p>
            </div>
          </div>
          <div class="flex items-center gap-3 rounded-lg border p-3">
            <FolderOpen class="h-5 w-5 text-primary shrink-0" />
            <div>
              <p class="text-sm font-medium">任务管理</p>
              <p class="text-xs text-muted-foreground">保存和管理你的建模任务历史</p>
            </div>
          </div>
          <div class="flex items-center gap-3 rounded-lg border p-3">
            <Download class="h-5 w-5 text-primary shrink-0" />
            <div>
              <p class="text-sm font-medium">论文导出</p>
              <p class="text-xs text-muted-foreground">导出完整建模方案和论文</p>
            </div>
          </div>
        </div>

        <!-- Terms -->
        <p class="mt-8 text-center text-xs text-muted-foreground">
          登录即表示你同意我们的
          <a href="#" class="text-primary hover:underline">服务条款</a>
          和
          <a href="#" class="text-primary hover:underline">隐私政策</a>
        </p>

        <!-- Back home -->
        <div class="mt-6 text-center">
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
import {
  Github,
  Shield,
  Zap,
  Users,
  Sigma,
  MessageSquare,
  FolderOpen,
  Download,
  ArrowLeft,
  Loader2,
} from "lucide-vue-next";
import { APP_NAME, GITHUB_LINK } from "@/utils/const";

const loading = ref(false);

function handleGithubLogin() {
  loading.value = true;
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID || "";
  if (!clientId) {
    alert("请先在 .env.development 中配置 VITE_GITHUB_CLIENT_ID");
    loading.value = false;
    return;
  }
  const redirectUri = encodeURIComponent(window.location.origin + "/auth/callback");
  const scope = "read:user user:email";
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  window.location.href = githubAuthUrl;
}
</script>
