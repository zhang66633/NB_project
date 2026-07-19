<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <div class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
            <Sigma class="h-4 w-4 text-primary-foreground" />
          </div>
          <span class="font-semibold text-sm">{{ APP_NAME }}</span>
        </div>
        <router-link
          to="/"
          class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft class="h-4 w-4" />
          返回首页
        </router-link>
      </div>
    </header>

    <main class="mx-auto max-w-3xl px-6 py-8">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <router-link to="/" class="hover:text-foreground transition-colors">首页</router-link>
        <ChevronRight class="h-3.5 w-3.5" />
        <router-link to="/example/0" class="hover:text-foreground transition-colors">例题</router-link>
        <ChevronRight class="h-3.5 w-3.5" />
        <span class="text-foreground truncate">{{ example.title || '加载中...' }}</span>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="space-y-4 animate-pulse">
        <div class="h-8 bg-muted rounded w-3/4" />
        <div class="h-4 bg-muted rounded w-1/2" />
        <div class="h-40 bg-muted rounded" />
      </div>

      <!-- Content -->
      <template v-else>
        <!-- Title & Metadata -->
        <div class="mb-6">
          <div class="flex items-center gap-2 mb-2">
            <span class="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium">
              {{ example.category }}
            </span>
            <span
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
              :class="difficultyClass"
            >
              {{ example.difficulty }}
            </span>
            <span class="text-xs text-muted-foreground">{{ example.competition }}</span>
          </div>
          <h1 class="text-2xl font-bold">{{ example.title }}</h1>
        </div>

        <!-- Problem Description -->
        <section class="mb-8">
          <h2 class="text-lg font-semibold mb-3">问题描述</h2>
          <div class="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card p-6">
            {{ example.description }}
          </div>
        </section>

        <!-- Analysis -->
        <section v-if="example.analysis" class="mb-8">
          <h2 class="text-lg font-semibold mb-3">问题分析</h2>
          <div
            class="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card p-6"
            v-html="renderedAnalysis"
          />
        </section>

        <!-- Model -->
        <section v-if="example.model" class="mb-8">
          <h2 class="text-lg font-semibold mb-3">模型建立</h2>
          <div
            class="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card p-6"
            v-html="renderedModel"
          />
        </section>

        <!-- Solution -->
        <section v-if="example.solution" class="mb-8">
          <h2 class="text-lg font-semibold mb-3">求解过程</h2>
          <div class="rounded-xl border bg-card overflow-hidden">
            <div
              class="prose prose-sm dark:prose-invert max-w-none p-6"
              v-html="renderedSolution"
            />
            <!-- Code block -->
            <div v-if="example.code" class="border-t bg-muted/30 p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-medium text-muted-foreground">Python 实现</span>
                <button
                  class="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs hover:bg-accent transition-colors"
                  @click="copyCode"
                >
                  <Copy class="h-3 w-3" />
                  复制
                </button>
              </div>
              <pre class="text-sm font-mono overflow-x-auto"><code>{{ example.code }}</code></pre>
            </div>
          </div>
        </section>

        <!-- Results -->
        <section v-if="example.results" class="mb-8">
          <h2 class="text-lg font-semibold mb-3">结果分析</h2>
          <div
            class="prose prose-sm dark:prose-invert max-w-none rounded-xl border bg-card p-6"
            v-html="renderedResults"
          />
        </section>

        <!-- Action -->
        <div class="flex items-center justify-center py-6 border-t">
          <button
            class="inline-flex items-center justify-center rounded-xl bg-primary px-8 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            @click="tryExample"
          >
            <Play class="h-4 w-4 mr-1.5" />
            尝试此例题
          </button>
        </div>

        <!-- Related examples -->
        <section v-if="relatedExamples.length > 0" class="border-t pt-8">
          <h2 class="text-lg font-semibold mb-4">相关例题</h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <div
              v-for="rel in relatedExamples"
              :key="rel.id"
              class="cursor-pointer rounded-xl border bg-card p-4 hover:shadow-md hover:border-primary/30 transition-all"
              @click="router.push(`/example/${rel.id}`)"
            >
              <h3 class="text-sm font-medium hover:text-primary transition-colors">{{ rel.title }}</h3>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs text-muted-foreground">{{ rel.category }}</span>
              </div>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import {
  Sigma,
  ArrowLeft,
  ChevronRight,
  Copy,
  Play,
} from "lucide-vue-next";
import { APP_NAME } from "@/utils/const";

marked.use(markedKatex({ throwOnError: false }));

const props = defineProps<{
  id: string;
}>();

const router = useRouter();
const loading = ref(true);

interface ExampleData {
  title: string;
  category: string;
  difficulty: string;
  competition: string;
  description: string;
  analysis?: string;
  model?: string;
  solution?: string;
  code?: string;
  results?: string;
}

const example = ref<ExampleData>({
  title: "",
  category: "",
  difficulty: "中等",
  competition: "",
  description: "",
});

const relatedExamples = ref<Array<{ id: number; title: string; category: string }>>([]);

const difficultyClass = computed(() => {
  switch (example.value.difficulty) {
    case "简单":
      return "bg-green-100 text-green-700";
    case "中等":
      return "bg-yellow-100 text-yellow-700";
    case "困难":
      return "bg-red-100 text-red-700";
    default:
      return "bg-muted text-muted-foreground";
  }
});

const renderedAnalysis = computed(() =>
  example.value.analysis ? marked.parse(example.value.analysis) : ""
);
const renderedModel = computed(() =>
  example.value.model ? marked.parse(example.value.model) : ""
);
const renderedSolution = computed(() =>
  example.value.solution ? marked.parse(example.value.solution) : ""
);
const renderedResults = computed(() =>
  example.value.results ? marked.parse(example.value.results) : ""
);

function copyCode() {
  if (example.value.code) {
    navigator.clipboard.writeText(example.value.code);
  }
}

function tryExample() {
  router.push({
    path: "/chat",
    query: {
      problem: `${example.value.title}\n\n${example.value.description}`,
      mode: "execute",
    },
  });
}

// Demo data - in production, fetch from API
const demos: Record<string, ExampleData> = {
  "1": {
    title: "配送中心选址优化",
    category: "优化问题",
    difficulty: "中等",
    competition: "2023 国赛 B 题",
    description:
      "某物流公司计划在 5 个备选地点中选择 2 个建立配送中心，为 10 个需求点提供服务。\n\n已知各备选地点到各需求点的运输距离和单位运输成本，以及各需求点的日需求量。目标是最小化总运输成本。",
    analysis:
      "这是一个典型的**设施选址问题**（Facility Location Problem），可建模为混合整数线性规划（MILP）。\n\n**决策变量**：\n- $x_{ij}$：从配送中心 $i$ 到需求点 $j$ 的运输量\n- $y_i$：是否在备选点 $i$ 建立配送中心（二元变量）\n\n**约束条件**：\n- 每个需求点的需求必须被满足\n- 配送中心容量限制\n- 只能选择 2 个配送中心",
    model:
      "## 数学模型\n\n**目标函数**：\n$$\\min Z = \\sum_{i=1}^{5}\\sum_{j=1}^{10} c_{ij} \\cdot d_{ij} \\cdot x_{ij}$$\n\n其中 $c_{ij}$ 为单位运输成本，$d_{ij}$ 为运输距离。\n\n**约束条件**：\n$$\\sum_{i=1}^{5} x_{ij} = D_j, \\quad \\forall j$$\n$$\\sum_{j=1}^{10} x_{ij} \\leq C_i \\cdot y_i, \\quad \\forall i$$\n$$\\sum_{i=1}^{5} y_i = 2$$\n$$x_{ij} \\geq 0, \\quad y_i \\in \\{0, 1\\}$$",
    code: 'from pulp import *\n\n# 定义问题\nprob = LpProblem("Facility_Location", LpMinimize)\n\n# 决策变量\nx = LpVariable.dicts("x", [(i,j) for i in range(5) for j in range(10)], lowBound=0)\ny = LpVariable.dicts("y", range(5), cat="Binary")\n\n# 目标函数\nprob += lpSum([cost[i][j] * dist[i][j] * x[i,j] for i in range(5) for j in range(10)])\n\n# 需求约束\nfor j in range(10):\n    prob += lpSum([x[i,j] for i in range(5)]) == demand[j]\n\n# 容量约束\nfor i in range(5):\n    prob += lpSum([x[i,j] for j in range(10)]) <= capacity[i] * y[i]\n\n# 数量约束\nprob += lpSum([y[i] for i in range(5)]) == 2\n\n# 求解\nprob.solve()',
    results:
      "求解结果显示，选择备选地点 2 和 4 建立配送中心，总运输成本为 125,430 元/天。\n\n**灵敏度分析**：\n- 需求波动 ±20% 的情况下，最优选址不变\n- 运输成本上升 10% 时，总成本按比例增加，但不影响选址决策",
  },
};

onMounted(async () => {
  loading.value = true;
  // Try demo data first, then fall back
  if (demos[props.id]) {
    example.value = demos[props.id];
    relatedExamples.value = [
      { id: 2, title: "城市交通流量预测", category: "预测问题" },
      { id: 3, title: "水资源质量评价", category: "评价问题" },
    ];
  } else {
    // In production: fetch from API
    example.value = {
      title: `例题 ${props.id}`,
      category: "综合问题",
      difficulty: "中等",
      competition: "",
      description: "该例题正在建设中，敬请期待...",
    };
  }
  loading.value = false;
});
</script>
