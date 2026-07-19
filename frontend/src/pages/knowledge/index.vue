<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="border-b">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div class="flex items-center gap-3">
          <router-link to="/" class="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← 首页
          </router-link>
          <span class="text-border">|</span>
          <div class="flex items-center gap-2">
            <Library class="h-4 w-4 text-primary" />
            <span class="font-semibold text-sm">知识库</span>
          </div>
        </div>
        <div class="flex items-center gap-3 text-xs text-muted-foreground">
          <span>📐 {{ stats.methods_count }} 方法</span>
          <span>📄 {{ stats.papers_count }} 论文</span>
          <span>📋 {{ stats.templates_count }} 模板</span>
        </div>
      </div>
    </header>

    <!-- Tabs -->
    <div class="mx-auto max-w-6xl px-6 pt-6">
      <div class="flex items-center gap-1 rounded-lg bg-muted p-1 w-fit">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="inline-flex items-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition-all"
          :class="activeTab === tab.value ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'"
          @click="activeTab = tab.value"
        >
          <component :is="tab.icon" class="h-4 w-4" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab 1: Search -->
    <section v-if="activeTab === 'search'" class="mx-auto max-w-3xl px-6 pt-6 pb-16">
      <div class="flex gap-2">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            v-model="query"
            type="text"
            placeholder="搜索方法、论文或模板... 例如: 线性规划、资源分配、时间序列"
            class="w-full rounded-xl border border-input bg-background pl-10 pr-4 py-2.5 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @keyup.enter="handleSearch"
          />
        </div>
        <button
          class="inline-flex items-center justify-center rounded-xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="!query.trim() || loading"
          @click="handleSearch"
        >
          <Loader2 v-if="loading" class="h-4 w-4 animate-spin" />
          <span v-else>搜索</span>
        </button>
      </div>
      <div class="flex items-center gap-3 mt-3 flex-wrap">
        <span class="text-xs text-muted-foreground">筛选:</span>
        <button v-for="opt in typeOptions" :key="opt.value"
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
          :class="filterType === opt.value ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
          @click="filterType = opt.value">{{ opt.label }}</button>
        <span class="text-xs text-muted-foreground">问题类型:</span>
        <button v-for="opt in problemTypeOptions" :key="opt.value"
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
          :class="filterProblemType === opt.value ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
          @click="filterProblemType = opt.value">{{ opt.label }}</button>
      </div>

      <div v-if="loading" class="space-y-4 mt-6">
        <div v-for="i in 3" :key="i" class="rounded-xl border bg-card p-5 space-y-3">
          <Skeleton class="h-4 w-2/3" />
          <Skeleton class="h-3 w-full" />
        </div>
      </div>
      <div v-else-if="searched && results.length === 0" class="text-center py-16">
        <Search class="h-12 w-12 mx-auto text-muted-foreground/40" />
        <p class="mt-4 text-muted-foreground">未找到与 "{{ lastQuery }}" 相关的结果</p>
      </div>
      <div v-else-if="!searched" class="text-center py-16">
        <Library class="h-12 w-12 mx-auto text-muted-foreground/40" />
        <p class="mt-4 text-muted-foreground">输入关键词搜索知识库</p>
      </div>
      <div v-else class="space-y-3 mt-6">
        <p class="text-sm text-muted-foreground">找到 {{ results.length }} 条结果</p>
        <div v-for="item in results" :key="item.id"
          class="group cursor-pointer rounded-xl border bg-card p-5 transition-all hover:shadow-md hover:border-primary/30"
          @click="openDetail(item)">
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium" :class="typeBadgeClass(item.type)">{{ typeLabel(item.type) }}</span>
                <span v-if="item.score !== null" class="text-xs text-muted-foreground">相关度 {{ ((item.score || 0) * 100).toFixed(0) }}%</span>
              </div>
              <h3 class="text-sm font-semibold truncate">{{ item.name || item.title }}</h3>
              <p class="text-xs text-muted-foreground mt-1.5 line-clamp-3">{{ item.snippet }}</p>
            </div>
            <ChevronRight class="h-4 w-4 shrink-0 text-muted-foreground/40 group-hover:text-muted-foreground mt-1" />
          </div>
        </div>
      </div>
    </section>

    <!-- Tab 2: Manage -->
    <section v-if="activeTab === 'manage'" class="mx-auto max-w-5xl px-6 pt-6 pb-16">
      <!-- Type selector -->
      <div class="flex items-center gap-2 mb-4">
        <span class="text-sm text-muted-foreground">类型:</span>
        <button v-for="opt in manageTypeOptions" :key="opt.value"
          class="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium transition-colors"
          :class="manageType === opt.value ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
          @click="manageType = opt.value">{{ opt.label }}</button>
        <span class="flex-1" />
        <button class="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs hover:bg-accent transition-colors"
          @click="loadManageList">
          <RefreshCw class="h-3 w-3" /> 刷新
        </button>
      </div>

      <!-- Entry list -->
      <div v-if="manageLoading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="rounded-xl border bg-card p-4"><Skeleton class="h-4 w-3/4" /></div>
      </div>
      <div v-else-if="manageEntries.length === 0" class="text-center py-12 border rounded-xl">
        <p class="text-muted-foreground">暂无{{ manageTypeLabel }}条目</p>
        <p class="text-xs text-muted-foreground/60 mt-1">切换到"导入知识"Tab 上传新内容</p>
      </div>
      <div v-else class="space-y-2">
        <div v-for="entry in manageEntries" :key="entry.id"
          class="flex items-center gap-3 rounded-xl border bg-card px-4 py-3 transition-all hover:border-primary/30 group">
          <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0"
            :class="manageTypeBadgeClass">&nbsp;{{ (manageTypeLabel as string).charAt(0) }}&nbsp;</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ entry.name || entry.title }}</p>
            <p class="text-xs text-muted-foreground">{{ entrySubtitle(entry) }}</p>
          </div>
          <div class="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <button class="inline-flex items-center justify-center rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              title="编辑" @click="openEditDialog(entry)">
              <Pencil class="h-3.5 w-3.5" />
            </button>
            <button class="inline-flex items-center justify-center rounded-md p-1.5 text-muted-foreground hover:bg-red-50 hover:text-red-600 transition-colors"
              title="删除" @click="confirmDelete(entry)">
              <Trash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <p class="text-xs text-muted-foreground text-center pt-2">共 {{ manageEntries.length }} 条</p>
      </div>

      <!-- Reindex button -->
      <div class="mt-8 pt-6 border-t text-center">
        <button class="inline-flex items-center gap-1.5 text-xs text-muted-foreground/50 hover:text-muted-foreground transition-colors"
          :disabled="reindexing" @click="handleReindex">
          <RefreshCw v-if="reindexing" class="h-3 w-3 animate-spin" />
          <Database v-else class="h-3 w-3" />
          {{ reindexing ? '重建索引中...' : '重建向量索引' }}
        </button>
      </div>
    </section>

    <!-- Tab 3: Import -->
    <section v-if="activeTab === 'import'" class="mx-auto max-w-3xl px-6 pt-6 pb-16">
      <div class="rounded-2xl border bg-card p-6">
        <h3 class="font-semibold mb-4 flex items-center gap-2">
          <Upload class="h-4 w-4" /> 导入知识
        </h3>
        <!-- Type selector -->
        <div class="flex items-center gap-2 mb-4">
          <span class="text-sm text-muted-foreground">类型:</span>
          <button v-for="opt in importTypeOptions" :key="opt.value"
            class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
            :class="importType === opt.value ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
            @click="importType = opt.value">{{ opt.label }}</button>
        </div>
        <!-- Text input -->
        <label class="block text-sm font-medium mb-2">粘贴原始文本内容</label>
        <textarea
          v-model="importText"
          rows="8"
          :placeholder="importPlaceholder"
          class="w-full resize-y rounded-xl border border-input bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
        <div class="flex items-center gap-2 mt-3">
          <input
            v-model="importName"
            type="text"
            placeholder="名称（可选，如: 粒子群算法）"
            class="flex-1 rounded-lg border border-input bg-background px-3 py-1.5 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          <button
            class="inline-flex items-center justify-center rounded-xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
            :disabled="!importText.trim() || extracting"
            @click="handleExtract"
          >
            <Loader2 v-if="extracting" class="h-4 w-4 mr-1.5 animate-spin" />
            <Sparkles v-else class="h-4 w-4 mr-1.5" />
            {{ extracting ? 'LLM 提取中...' : 'LLM 提取并预览' }}
          </button>
        </div>

        <!-- Error -->
        <div v-if="extractError" class="mt-4 rounded-lg border border-red-200 bg-red-50 p-3">
          <p class="text-sm text-red-700">{{ extractError }}</p>
        </div>

        <!-- Preview -->
        <div v-if="extractPreview" class="mt-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-green-600">✓ 提取完成</span>
          </div>
          <pre class="rounded-lg bg-zinc-950 p-4 text-xs text-zinc-300 overflow-auto max-h-96">{{ extractPreview }}</pre>
          <div class="flex items-center gap-2 mt-3">
            <button
              class="inline-flex items-center justify-center rounded-xl bg-green-600 px-5 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors disabled:opacity-50"
              :disabled="saving"
              @click="handleSaveExtracted"
            >
              <Check v-if="!saving" class="h-4 w-4 mr-1" />
              <Loader2 v-else class="h-4 w-4 mr-1 animate-spin" />
              {{ saving ? '保存中...' : '保存到知识库' }}
            </button>
            <button
              class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm hover:bg-accent transition-colors"
              @click="extractPreview = ''; extractError = ''">
              <RotateCcw class="h-4 w-4 mr-1" />重新提取
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Detail Dialog -->
    <Dialog :open="!!selectedItem" @update:open="selectedItem = null">
      <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium" :class="typeBadgeClass(selectedItem?.type || '')">
              {{ typeLabel(selectedItem?.type || '') }}
            </span>
            {{ selectedItem?.name || selectedItem?.title }}
          </DialogTitle>
        </DialogHeader>
        <div v-if="detailLoading" class="space-y-3 py-4">
          <Skeleton class="h-4 w-full" /><Skeleton class="h-4 w-5/6" />
        </div>
        <div v-else-if="detail?.type === 'method_card'" class="space-y-4 py-2 text-sm">
          <div><h4 class="font-semibold mb-1">分类</h4>
            <div class="flex flex-wrap gap-1"><span v-for="c in (detail.data as any).category" :key="c" class="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs">{{ c }}</span></div>
          </div>
          <div><h4 class="font-semibold mb-1">核心原理</h4><p class="text-muted-foreground">{{ (detail.data as any).principle }}</p></div>
          <div><h4 class="font-semibold mb-1">适用条件</h4><ul class="list-disc list-inside text-muted-foreground"><li v-for="c in (detail.data as any).applicable_when" :key="c">{{ c }}</li></ul></div>
          <div><h4 class="font-semibold mb-1">典型场景</h4><ul class="list-disc list-inside text-muted-foreground"><li v-for="s in (detail.data as any).typical_scenarios" :key="s">{{ s }}</li></ul></div>
        </div>
        <div v-else-if="detail?.type === 'paper'" class="space-y-4 py-2 text-sm">
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs">{{ (detail.data as any).competition }}</span>
            <span class="text-xs text-muted-foreground">{{ (detail.data as any).year }}年{{ (detail.data as any).problem_id }}题</span>
            <span class="text-xs text-amber-500">{{ '★'.repeat((detail.data as any).quality_rating || 3) }}</span>
          </div>
          <div><h4 class="font-semibold mb-1">建模思路</h4><p class="text-muted-foreground">{{ (detail.data as any).model?.approach }}</p></div>
          <div><h4 class="font-semibold mb-1">可学之处</h4><p class="text-muted-foreground">{{ (detail.data as any).evaluation?.lessons }}</p></div>
        </div>
        <div v-else-if="detail?.type === 'template'" class="space-y-4 py-2 text-sm">
          <div><h4 class="font-semibold mb-2">分析步骤 ({{ (detail.data as any).steps?.length || 0 }}步)</h4>
            <div class="space-y-3"><div v-for="s in (detail.data as any).steps" :key="s.step" class="rounded-lg border p-3">
              <h5 class="font-semibold text-sm">步骤{{ s.step }}: {{ s.name }}</h5>
              <ul v-if="s.checklist?.length" class="list-disc list-inside text-xs text-muted-foreground mt-1"><li v-for="c in s.checklist" :key="c">{{ c }}</li></ul>
            </div></div>
          </div>
        </div>
        <DialogFooter><DialogClose class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm hover:bg-accent">关闭</DialogClose></DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Edit Dialog -->
    <Dialog :open="showEditDialog" @update:open="showEditDialog = $event">
      <DialogContent class="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>编辑{{ manageTypeLabel }}: {{ editForm.name || editForm.title }}</DialogTitle>
        </DialogHeader>
        <div class="space-y-3 py-2 text-sm">
          <div v-if="editForm.id"><span class="text-xs text-muted-foreground">ID: {{ editForm.id }} (不可修改)</span></div>

          <!-- Method fields -->
          <template v-if="manageType === 'method'">
            <div><label class="text-xs font-medium">名称</label>
              <input v-model="editForm.name" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">分类 (逗号分隔)</label>
              <input v-model="editForm.categoryStr" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">核心原理</label>
              <textarea v-model="editForm.principle" rows="4" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">适用条件 (每行一个)</label>
              <textarea v-model="editForm.applicableWhenStr" rows="3" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">典型场景 (每行一个)</label>
              <textarea v-model="editForm.typicalScenariosStr" rows="3" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
          </template>

          <!-- Paper fields -->
          <template v-if="manageType === 'paper'">
            <div class="grid grid-cols-3 gap-2">
              <div><label class="text-xs font-medium">年份</label><input v-model.number="editForm.year" type="number" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
              <div><label class="text-xs font-medium">竞赛</label><input v-model="editForm.competition" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
              <div><label class="text-xs font-medium">题号</label><input v-model="editForm.problem_id" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            </div>
            <div><label class="text-xs font-medium">标题</label><input v-model="editForm.title" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">建模思路</label>
              <textarea v-model="editForm.approach" rows="3" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">可学之处</label>
              <textarea v-model="editForm.lessons" rows="2" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">质量评分 (1-5)</label>
              <input v-model.number="editForm.quality_rating" type="number" min="1" max="5" class="w-20 rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
          </template>

          <!-- Template fields -->
          <template v-if="manageType === 'template'">
            <div><label class="text-xs font-medium">名称</label>
              <input v-model="editForm.name" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
            <div><label class="text-xs font-medium">适用类型 (逗号分隔)</label>
              <input v-model="editForm.applicableToStr" class="w-full rounded-lg border px-3 py-1.5 text-sm mt-1" /></div>
          </template>
        </div>
        <DialogFooter>
          <button class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm hover:bg-accent" @click="showEditDialog = false">取消</button>
          <button class="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            :disabled="editSaving" @click="handleEditSave">
            <Loader2 v-if="editSaving" class="h-4 w-4 mr-1 animate-spin" />{{ editSaving ? '保存中...' : '保存' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirm Dialog -->
    <Dialog :open="showDeleteConfirm" @update:open="showDeleteConfirm = $event">
      <DialogContent class="max-w-sm">
        <DialogHeader>
          <DialogTitle>确认删除</DialogTitle>
          <DialogDescription>确定要删除 "{{ deleteTarget?.name || deleteTarget?.title }}"? 此操作不可撤销。</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <button class="inline-flex items-center justify-center rounded-lg border px-4 py-2 text-sm hover:bg-accent" @click="showDeleteConfirm = false">取消</button>
          <button class="inline-flex items-center justify-center rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
            :disabled="deleting" @click="handleDeleteConfirm">
            <Loader2 v-if="deleting" class="h-4 w-4 mr-1 animate-spin" />{{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  Library, Search, Loader2, ChevronRight, RefreshCw, Database,
  Upload, Sparkles, Check, RotateCcw, Pencil, Trash2, Layers, Plus,
} from "lucide-vue-next";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  searchKB, getKBStats, reindexKB, getMethod, getPaper, getTemplate,
  listMethods, listPapers, listTemplates,
  uploadKnowledge, getExtractionJob,
  updateMethod, deleteMethod, updatePaper, deletePaper, updateTemplate, deleteTemplate,
  type SearchResult as ApiSearchResult, type KBStats, type MethodCardSummary, type PaperSummary, type TemplateSummary,
} from "@/apis/knowledgeApi";

// ── tabs ──────────────────────────────────────────────────────────

const tabs = [
  { value: "search", label: "检索知识", icon: Search },
  { value: "manage", label: "管理知识", icon: Layers },
  { value: "import", label: "导入知识", icon: Upload },
];
const activeTab = ref("search");

// ── shared ────────────────────────────────────────────────────────

const stats = ref<KBStats>({ methods_count: 0, papers_count: 0, templates_count: 0, total: 0 });
const reindexing = ref(false);

function typeLabel(t: string) {
  return { method_card: "方法卡片", paper: "真题论文", template: "框架模板" }[t] || t;
}
function typeBadgeClass(t: string) {
  return { method_card: "bg-blue-100 text-blue-700", paper: "bg-purple-100 text-purple-700", template: "bg-green-100 text-green-700" }[t] || "bg-muted";
}

// ── Tab 1: Search ────────────────────────────────────────────────

const query = ref(""); const lastQuery = ref(""); const results = ref<ApiSearchResult[]>([]);
const loading = ref(false); const searched = ref(false);
const filterType = ref(""); const filterProblemType = ref("");
const selectedItem = ref<ApiSearchResult | null>(null);
const detailLoading = ref(false);
const detail = ref<{ type: string; data: Record<string, unknown> } | null>(null);

const typeOptions = [
  { label: "全部", value: "" }, { label: "方法卡片", value: "method_card" },
  { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" },
];
const problemTypeOptions = [
  { label: "全部", value: "" }, { label: "优化", value: "optimization" },
  { label: "预测", value: "prediction" }, { label: "评价", value: "evaluation" },
  { label: "统计", value: "statistics" },
];

async function handleSearch() {
  if (!query.value.trim()) return;
  loading.value = true; searched.value = true; lastQuery.value = query.value.trim();
  try {
    const res = await searchKB({ q: query.value.trim(), type: filterType.value || undefined, problem_type: filterProblemType.value || undefined, k: 10 });
    results.value = res.data.results;
  } catch { results.value = []; }
  finally { loading.value = false; }
}

async function openDetail(item: ApiSearchResult) {
  selectedItem.value = item; detailLoading.value = true; detail.value = null;
  try {
    if (item.type === "method_card") { const r = await getMethod(item.id); detail.value = { type: "method_card", data: r.data as any }; }
    else if (item.type === "paper") { const r = await getPaper(item.id); detail.value = { type: "paper", data: r.data as any }; }
    else if (item.type === "template") { const r = await getTemplate(item.id); detail.value = { type: "template", data: r.data as any }; }
  } catch { /* ignore */ }
  finally { detailLoading.value = false; }
}

// ── Tab 2: Manage ────────────────────────────────────────────────

const manageType = ref("method");
const manageEntries = ref<(MethodCardSummary | PaperSummary | TemplateSummary & { title?: string })[]>([]);
const manageLoading = ref(false);
const showEditDialog = ref(false);
const showDeleteConfirm = ref(false);
const deleteTarget = ref<any>(null);
const deleting = ref(false);
const editSaving = ref(false);
const editForm = ref<Record<string, any>>({});

const manageTypeOptions = [
  { label: "方法卡片", value: "method" }, { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" },
];
const manageTypeLabel = computed(() => ({ method: "方法", paper: "论文", template: "模板" }[manageType.value]));
const manageTypeBadgeClass = computed(() => ({ method: "bg-blue-100 text-blue-700", paper: "bg-purple-100 text-purple-700", template: "bg-green-100 text-green-700" }[manageType.value]));

function entrySubtitle(entry: any) {
  if (manageType.value === "method") return (entry.category || []).join(", ");
  if (manageType.value === "paper") return `${entry.year || ""} ${entry.competition || ""} ${entry.problem_id || ""} ★${entry.quality_rating || 3}`;
  return `${entry.steps_count || 0} 个步骤`;
}

async function loadManageList() {
  manageLoading.value = true;
  try {
    if (manageType.value === "method") { const r = await listMethods(); manageEntries.value = r.data as any; }
    else if (manageType.value === "paper") { const r = await listPapers(); manageEntries.value = r.data as any; }
    else { const r = await listTemplates(); manageEntries.value = r.data as any; }
  } catch { manageEntries.value = []; }
  finally { manageLoading.value = false; }
}

function openEditDialog(entry: any) {
  editForm.value = { ...entry };
  // Convert arrays to editable strings
  if (manageType.value === "method") {
    editForm.value.categoryStr = (entry.category || []).join(", ");
    editForm.value.applicableWhenStr = (entry.applicable_when || []).join("\n");
    editForm.value.typicalScenariosStr = (entry.typical_scenarios || []).join("\n");
  }
  if (manageType.value === "template") {
    editForm.value.applicableToStr = (entry.applicable_to || []).join(", ");
  }
  // Paper nested fields
  if (manageType.value === "paper") {
    editForm.value.approach = entry.model?.approach || "";
    editForm.value.lessons = entry.evaluation?.lessons || "";
  }
  showEditDialog.value = true;
}

async function handleEditSave() {
  editSaving.value = true;
  try {
    const id = editForm.value.id;
    let data: Record<string, any> = { ...editForm.value };
    // Convert strings back to arrays
    if (manageType.value === "method") {
      data.category = (editForm.value.categoryStr || "").split(",").map((s: string) => s.trim()).filter(Boolean);
      data.applicable_when = (editForm.value.applicableWhenStr || "").split("\n").filter(Boolean);
      data.typical_scenarios = (editForm.value.typicalScenariosStr || "").split("\n").filter(Boolean);
      delete data.categoryStr; delete data.applicableWhenStr; delete data.typicalScenariosStr;
      await updateMethod(id, data);
    } else if (manageType.value === "paper") {
      data.model = { approach: editForm.value.approach || "", innovation: editForm.value.model?.innovation || "", solution_method: editForm.value.model?.solution_method || "" };
      data.evaluation = { strengths: editForm.value.evaluation?.strengths || [], weaknesses: editForm.value.evaluation?.weaknesses || [], lessons: editForm.value.lessons || "" };
      delete data.approach; delete data.lessons;
      await updatePaper(id, data);
    } else {
      data.applicable_to = (editForm.value.applicableToStr || "").split(",").map((s: string) => s.trim()).filter(Boolean);
      delete data.applicableToStr;
      await updateTemplate(id, data);
    }
    showEditDialog.value = false;
    await loadManageList();
    await loadStats();
  } catch (e: any) { alert(`保存失败: ${e?.response?.data?.detail || e}`); }
  finally { editSaving.value = false; }
}

function confirmDelete(entry: any) {
  deleteTarget.value = entry;
  showDeleteConfirm.value = true;
}

async function handleDeleteConfirm() {
  deleting.value = true;
  try {
    const id = deleteTarget.value.id;
    if (manageType.value === "method") await deleteMethod(id);
    else if (manageType.value === "paper") await deletePaper(id);
    else await deleteTemplate(id);
    showDeleteConfirm.value = false;
    deleteTarget.value = null;
    await loadManageList();
    await loadStats();
  } catch (e: any) { alert(`删除失败: ${e?.response?.data?.detail || e}`); }
  finally { deleting.value = false; }
}

watch(manageType, () => { loadManageList(); });

// ── Tab 3: Import ────────────────────────────────────────────────

const importType = ref("method");
const importText = ref("");
const importName = ref("");
const extracting = ref(false);
const saving = ref(false);
const extractPreview = ref("");
const extractError = ref("");

const importTypeOptions = [
  { label: "方法卡片", value: "method" }, { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" },
];
const importPlaceholder = computed(() => {
  const m: Record<string, string> = {
    method: "粘贴方法描述...\n例如: 粒子群优化算法(PSO)是一种基于群体智能的启发式优化算法。由Kennedy和Eberhart于1995年提出...",
    paper: "粘贴论文内容...\n例如: 2024年国赛A题优秀论文。本文基于混合整数规划模型求解无人机调度问题...",
    template: "粘贴分析框架描述...\n例如: 微分方程问题分析框架。第一步: 问题识别...",
  };
  return m[importType.value] || "粘贴原始文本内容...";
});

async function handleExtract() {
  if (!importText.value.trim()) return;
  extracting.value = true; extractError.value = ""; extractPreview.value = "";
  try {
    const res = await uploadKnowledge({
      text: importText.value.trim(),
      kb_type: importType.value,
      name: importName.value,
    });
    const jobId = res.data.job_id;
    // Poll until complete
    let attempts = 0;
    while (attempts < 60) {
      await new Promise(r => setTimeout(r, 1000));
      const job = await getExtractionJob(jobId);
      if (job.data.status === "completed") {
        extractPreview.value = job.data.result?.yaml_content || "";
        break;
      }
      if (job.data.status === "error") {
        extractError.value = job.data.error || "提取失败";
        break;
      }
      attempts++;
    }
    if (attempts >= 60) extractError.value = "提取超时，请重试";
  } catch (e: any) {
    extractError.value = `请求失败: ${e?.response?.data?.detail || e}`;
  }
  finally { extracting.value = false; }
}

async function handleSaveExtracted() {
  // Already saved by the backend during extraction
  saving.value = true;
  await loadStats();
  await new Promise(r => setTimeout(r, 500));
  extractPreview.value = "";
  extractError.value = "";
  importText.value = "";
  importName.value = "";
  saving.value = false;
  alert("已保存到知识库并完成索引！切换到「检索知识」Tab 可搜索验证。");
}

async function handleReindex() {
  reindexing.value = true;
  try {
    const res = await reindexKB();
    alert(res.data.message);
    await loadStats();
  } catch { alert("重建索引失败"); }
  finally { reindexing.value = false; }
}

// ── lifecycle ─────────────────────────────────────────────────────

async function loadStats() {
  try { const r = await getKBStats(); stats.value = r.data; } catch { /* ignore */ }
}

watch(activeTab, (tab) => {
  if (tab === "manage") loadManageList();
});

onMounted(() => { loadStats(); });
</script>
