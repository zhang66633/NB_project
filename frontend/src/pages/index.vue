<template>
  <div class="bg-grid-paper min-h-full">
    <div class="mx-auto max-w-4xl px-6 sm:px-10">

      <!-- 标题区:大留白,衬线大标题 + italic 副标题,左对齐 -->
      <header class="pt-20 pb-24 sm:pt-28 sm:pb-32">
        <p class="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground mb-6">
          ·0 &nbsp; 工作台
        </p>
        <h1 class="font-display text-5xl sm:text-6xl font-medium tracking-tight leading-[1.05]">
          数学建模
        </h1>
        <p class="font-display italic text-2xl sm:text-3xl text-muted-foreground mt-3 leading-[1.2] pb-1">
          一份正在演算的手册
        </p>
        <p class="mt-8 text-base text-muted-foreground max-w-xl leading-relaxed">
          选择模式进入对话。教学模式以引导提问培养建模思维,方案模式结构化输出完整解题流程。
          所有推理与代码可追溯,像翻阅一份带批注的研究笔记。
        </p>
      </header>

      <!-- ·1 模式:章节列表式,左描述 + 右公式装饰 -->
      <section class="pb-24">
        <div class="section-rule mb-12">
          <span class="font-mono text-xs tracking-wider">·1 &nbsp; 开始</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-5 gap-12 lg:gap-16">
          <!-- 教学模式:占 3 -->
          <article class="lg:col-span-3">
            <div class="flex items-baseline gap-3 mb-3">
              <span class="font-mono text-xs text-primary">·1.1</span>
              <h2 class="font-display text-2xl font-medium">教学模式</h2>
            </div>
            <p class="text-sm text-muted-foreground leading-relaxed max-w-md mb-5">
              苏格拉底式引导提问,逐步建立建模思维。适合日常训练与备赛学习,留下完整推理痕迹。
            </p>
            <p class="font-mono text-xs text-muted-foreground mb-6">
              <span class="text-foreground/60">示例问题:</span>
              如何在总运输成本最小化时满足各节点需求?
            </p>
            <button
              class="group inline-flex items-center gap-2 rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background transition-transform hover:scale-[0.98] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              @click="enterChat('teach')"
            >
              开始学习
              <ArrowRight class="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </button>
          </article>

          <!-- 公式装饰块:占 2,像论文里的公式 -->
          <aside class="lg:col-span-2 lg:border-l lg:border-border lg:pl-8">
            <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-3">
              典型形式
            </p>
            <pre class="font-mono text-xs leading-relaxed text-muted-foreground whitespace-pre-wrap">min  Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ

s.t.  Σᵢ xᵢⱼ = Dⱼ,  ∀j ∈ J
       xᵢⱼ ∈ {0, 1}</pre>
            <p class="font-mono text-[10px] text-muted-foreground/70 mt-3">
              [mc_008] 运输问题 · 整数规划
            </p>
          </aside>
        </div>

        <!-- 方案模式:第二行,反向(左公式右描述)打破对称 -->
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-12 lg:gap-16 mt-16">
          <aside class="lg:col-span-2 lg:order-1 lg:border-r lg:border-border lg:pr-8">
            <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-3">
              输出结构
            </p>
            <pre class="font-mono text-xs leading-relaxed text-muted-foreground whitespace-pre-wrap">1. 问题重述与假设
2. 模型建立
3. 求解与代码
4. 结果分析
5. 论文撰写</pre>
          </aside>
          <article class="lg:col-span-3 lg:order-2">
            <div class="flex items-baseline gap-3 mb-3">
              <span class="font-mono text-xs text-primary">·1.2</span>
              <h2 class="font-display text-2xl font-medium">方案模式</h2>
            </div>
            <p class="text-sm text-muted-foreground leading-relaxed max-w-md mb-5">
              结构化输出完整建模方案,含代码执行、结果验证与论文。适合限时竞赛与正式提交。
            </p>
            <button
              class="group inline-flex items-center gap-2 rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background transition-transform hover:scale-[0.98] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              @click="enterChat('execute')"
            >
              开始建模
              <ArrowRight class="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </button>
          </article>
        </div>
      </section>

      <!-- ·2 模块:紧凑列表式,divide-y,非图标卡片 -->
      <section class="pb-24">
        <div class="section-rule mb-8">
          <span class="font-mono text-xs tracking-wider">·2 &nbsp; 模块</span>
        </div>
        <ul class="divide-y divide-border">
          <li v-for="mod in modules" :key="mod.path">
            <button
              class="group flex w-full items-center gap-6 py-4 text-left transition-colors"
              @click="router.push(mod.path)"
            >
              <span class="font-mono text-xs text-muted-foreground w-8 shrink-0">{{ mod.num }}</span>
              <span class="font-display text-lg font-medium w-28 shrink-0 transition-colors group-hover:text-primary">
                {{ mod.label }}
              </span>
              <span class="text-sm text-muted-foreground flex-1 truncate">{{ mod.desc }}</span>
              <ArrowRight class="h-4 w-4 text-muted-foreground/50 transition-all group-hover:text-primary group-hover:translate-x-1 shrink-0" />
            </button>
          </li>
        </ul>
      </section>

      <!-- §3 知识库:等宽大数字横向,无框 -->
      <section v-if="statsReady" class="pb-20">
        <div class="section-rule mb-10">
          <span class="font-mono text-xs tracking-wider">·3 &nbsp; 知识库</span>
        </div>
        <div class="grid grid-cols-3 gap-8">
          <div v-for="s in statItems" :key="s.key">
            <p class="font-mono text-4xl sm:text-5xl font-medium tabular-nums leading-none">{{ s.value }}</p>
            <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground mt-3">{{ s.label }}</p>
          </div>
        </div>
      </section>

      <!-- 脚注:游客提示,像论文脚注 -->
      <footer class="border-t border-border py-10 mb-8">
        <p class="font-mono text-xs text-muted-foreground/80 leading-relaxed max-w-2xl">
          <span class="text-primary">†</span> &nbsp;
          当前为本地游客模式,对话与任务保存在本机。如需云端同步或多端协作,可在右上角设置中配置。
        </p>
      </footer>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight } from "lucide-vue-next";
import { getKBStats, type KBStats } from "@/apis/knowledgeApi";

const router = useRouter();

const statsReady = ref(false);

const modules = [
  { num: "§2", label: "对话", desc: "与智能体交互,实时推进建模", path: "/chat" },
  { num: "§3", label: "任务", desc: "查看建模任务的状态与产物", path: "/task/0" },
  { num: "§4", label: "知识库", desc: "方法卡片、真题与模板套路", path: "/knowledge" },
  { num: "§5", label: "例题", desc: "浏览示例与解析,参照学习", path: "/example/1" },
];

const statItems = ref([
  { key: "methods", label: "方法卡片", value: 0 },
  { key: "papers", label: "真题论文", value: 0 },
  { key: "templates", label: "模板套路", value: 0 },
]);

function enterChat(mode: "teach" | "execute") {
  router.push({ path: "/chat", query: { mode } });
}

onMounted(async () => {
  try {
    const data = await getKBStats();
    statItems.value = [
      { key: "methods", label: "方法卡片", value: data.methods_count },
      { key: "papers", label: "真题论文", value: data.papers_count },
      { key: "templates", label: "模板套路", value: data.templates_count },
    ];
    statsReady.value = true;
  } catch {
    statsReady.value = false;
  }
});
</script>
