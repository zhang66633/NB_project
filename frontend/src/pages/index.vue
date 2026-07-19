<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
            <Sigma class="h-4 w-4 text-primary-foreground" />
          </div>
          <span class="font-semibold text-sm">{{ APP_NAME }}</span>
        </div>
        <div class="flex items-center gap-3">
          <router-link
            to="/knowledge"
            class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <Library class="h-4 w-4" />
            <span class="hidden sm:inline">知识库</span>
          </router-link>
          <a
            :href="GITHUB_LINK"
            target="_blank"
            class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <Github class="h-4 w-4" />
            <span class="hidden sm:inline">GitHub</span>
          </a>
          <router-link
            to="/login"
            class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
          >
            登录
          </router-link>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="mx-auto max-w-4xl px-6 pt-16 pb-12 text-center">
      <h1 class="text-4xl font-bold tracking-tight sm:text-5xl">
        数学建模
        <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          多智能体
        </span>
        辅助系统
      </h1>
      <p class="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
        {{ APP_DESC }} — 基于 LangGraph 多智能体编排，支持教学模式与方案输出双模式，
        帮助您高效解决各类数学建模问题。
      </p>
    </section>

    <!-- Mode Cards -->
    <section class="mx-auto max-w-4xl px-6 pb-8">
      <div class="grid gap-4 sm:grid-cols-2">
        <!-- Teach mode -->
        <div
          class="group cursor-pointer rounded-2xl border-2 p-6 transition-all hover:border-green-300 hover:shadow-lg"
          :class="selectedMode === 'teach' ? 'border-green-500 bg-green-50/50' : 'border-border bg-card'"
          @click="selectedMode = 'teach'"
        >
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-green-100">
              <GraduationCap class="h-6 w-6 text-green-600" />
            </div>
            <div class="text-left">
              <h3 class="font-semibold text-lg">教学模式</h3>
              <p class="text-sm text-muted-foreground mt-1">
                苏格拉底式引导提问，逐步培养建模思维。适合日常训练与备赛学习。
              </p>
            </div>
          </div>
          <div class="mt-4 flex items-center gap-2 text-sm text-green-600">
            <Lightbulb class="h-4 w-4" />
            <span>引导式学习 · 思维展开 · 原理讲解</span>
          </div>
        </div>

        <!-- Execute mode -->
        <div
          class="group cursor-pointer rounded-2xl border-2 p-6 transition-all hover:border-blue-300 hover:shadow-lg"
          :class="selectedMode === 'execute' ? 'border-blue-500 bg-blue-50/50' : 'border-border bg-card'"
          @click="selectedMode = 'execute'"
        >
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-100">
              <FileText class="h-6 w-6 text-blue-600" />
            </div>
            <div class="text-left">
              <h3 class="font-semibold text-lg">方案输出模式</h3>
              <p class="text-sm text-muted-foreground mt-1">
                接收问题，结构化输出完整建模方案。适合实战解题与竞赛冲刺。
              </p>
            </div>
          </div>
          <div class="mt-4 flex items-center gap-2 text-sm text-blue-600">
            <Zap class="h-4 w-4" />
            <span>完整方案 · 代码执行 · 论文输出</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Problem Input -->
    <section class="mx-auto max-w-3xl px-6 pb-8">
      <div class="rounded-2xl border bg-card p-6 shadow-sm">
        <label class="block text-sm font-medium mb-2">
          输入你的数学建模问题
        </label>
        <textarea
          v-model="problem"
          rows="4"
          placeholder="例如：某城市需要在 5 个备选地点中选择 2 个建立配送中心，以最小化总运输成本。已知各地点到 10 个需求点的距离和需求量..."
          class="w-full resize-none rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
        <div class="flex items-center justify-between mt-3">
          <div class="flex items-center gap-2">
            <span
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="selectedMode === 'execute' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'"
            >
              {{ selectedMode === 'execute' ? '方案输出模式' : '教学模式' }}
            </span>
            <button
              class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs text-muted-foreground hover:bg-muted transition-colors"
              @click="toggleMode"
            >
              <ArrowLeftRight class="h-3 w-3" />
              切换
            </button>
          </div>
          <button
            class="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
            :disabled="!problem.trim() || submitting"
            @click="handleSubmit"
          >
            <Send v-if="!submitting" class="h-4 w-4 mr-1.5" />
            <Loader2 v-else class="h-4 w-4 mr-1.5 animate-spin" />
            {{ submitting ? '提交中...' : '开始建模' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Quick Examples -->
    <section class="mx-auto max-w-6xl px-6 pb-16">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">快速示例</h2>
        <router-link to="/example/0" class="text-sm text-primary hover:underline">
          查看全部
        </router-link>
      </div>
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="example in quickExamples"
          :key="example.id"
          class="group cursor-pointer rounded-xl border bg-card p-4 transition-all hover:shadow-md hover:border-primary/30"
          @click="selectExample(example)"
        >
          <span class="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground mb-2">
            {{ example.category }}
          </span>
          <h3 class="text-sm font-medium group-hover:text-primary transition-colors line-clamp-2">
            {{ example.title }}
          </h3>
          <p class="text-xs text-muted-foreground mt-1.5 line-clamp-2">
            {{ example.description }}
          </p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t py-8 text-center text-sm text-muted-foreground">
      <p>Built with Vue 3 + shadcn-vue + Tailwind CSS | 数学建模多智能体辅助系统</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  Sigma,
  Github,
  Library,
  GraduationCap,
  FileText,
  Lightbulb,
  Zap,
  ArrowLeftRight,
  Send,
  Loader2,
} from "lucide-vue-next";
import { APP_NAME, APP_DESC, GITHUB_LINK } from "@/utils/const";
import { TaskMode } from "@/utils/enum";

const router = useRouter();

const problem = ref("");
const selectedMode = ref<"teach" | "execute">("teach");
const submitting = ref(false);

const quickExamples = [
  {
    id: 1,
    title: "配送中心选址优化",
    category: "优化问题",
    description: "在多个备选地点中选择最佳配送中心位置，最小化运输成本。",
  },
  {
    id: 2,
    title: "城市交通流量预测",
    category: "预测问题",
    description: "基于历史数据预测未来交通流量，优化信号灯配时方案。",
  },
  {
    id: 3,
    title: "水资源质量评价",
    category: "评价问题",
    description: "建立综合评价模型，对多个水域的水质进行排名和分类。",
  },
];

function toggleMode() {
  selectedMode.value = selectedMode.value === "teach" ? "execute" : "teach";
}

function selectExample(example: { title: string; description: string }) {
  problem.value = `${example.title}\n\n${example.description}`;
}

async function handleSubmit() {
  if (!problem.value.trim()) return;
  submitting.value = true;
  try {
    // Navigate to chat with the problem as query param
    router.push({
      path: "/chat",
      query: {
        problem: problem.value,
        mode: selectedMode.value,
      },
    });
  } finally {
    submitting.value = false;
  }
}
</script>
