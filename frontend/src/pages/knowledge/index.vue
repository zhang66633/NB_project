<template>
  <div class="h-full overflow-y-auto bg-grid-paper">
    <div class="mx-auto max-w-4xl px-6 sm:px-10 py-12 sm:py-16">
        <!-- 标题区:§标记 + 衬线,去掉 em-dash -->
        <p class="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground mb-4">§4 &nbsp; 知识库</p>
        <h1 class="font-display text-3xl sm:text-4xl font-medium tracking-tight">方法卡片、真题与模板</h1>
        <p class="mt-2 text-sm text-muted-foreground">检索已有知识,管理条目,或从原始文本导入新内容。</p>

        <!-- Tabs:章节式等宽标签 + 下划线高亮,无胶囊背景 -->
        <div class="flex items-center gap-6 border-b mt-8 mb-8">
          <button v-for="(tab, i) in tabs" :key="tab.value"
            class="relative flex items-center gap-2 py-3 text-sm transition-colors"
            :class="activeTab === tab.value ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'"
            @click="activeTab = tab.value">
            <span class="font-mono text-[10px] text-muted-foreground/70">·4.{{ i + 1 }}</span>
            <span :class="activeTab === tab.value ? 'font-display font-medium' : ''">{{ tab.label }}</span>
            <span v-if="activeTab === tab.value" class="absolute left-0 right-0 -bottom-px h-px bg-primary"></span>
          </button>
        </div>

        <!-- ==================== TAB 1: 检索知识 ==================== -->
        <div v-if="activeTab === 'search'">
          <div class="flex gap-2 mb-5">
            <div class="relative flex-1">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input v-model="searchQuery" type="text" placeholder="搜索方法、论文或模板..."
                class="w-full rounded-md border border-border bg-background pl-10 pr-4 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                @keyup.enter="doSearch" />
            </div>
            <button class="inline-flex items-center rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background hover:bg-foreground/90 disabled:opacity-50 transition-transform active:scale-[0.98]"
              :disabled="!searchQuery.trim() || searchLoading" @click="doSearch">
              <Loader2 v-if="searchLoading" class="h-4 w-4 animate-spin" /><span v-else>搜索</span>
            </button>
          </div>
          <!-- 筛选:等宽小标签,非胶囊 -->
          <div class="flex flex-wrap items-center gap-x-5 gap-y-2 mb-6">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">类型</span>
            <button v-for="o in typeOpts" :key="o.value"
              class="font-mono text-[10px] uppercase tracking-wider transition-colors"
              :class="searchFilter === o.value ? 'text-primary' : 'text-muted-foreground/60 hover:text-foreground'"
              @click="searchFilter = o.value">{{ o.label }}</button>
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground ml-2">问题</span>
            <button v-for="o in probOpts" :key="o.value"
              class="font-mono text-[10px] uppercase tracking-wider transition-colors"
              :class="searchProblem === o.value ? 'text-primary' : 'text-muted-foreground/60 hover:text-foreground'"
              @click="searchProblem = o.value">{{ o.label }}</button>
          </div>

          <div v-if="searchLoading" class="space-y-3"><div v-for="i in 3" :key="i" class="rounded-md border border-border p-5"><Skeleton class="h-4 w-2/3" /><Skeleton class="h-3 w-full mt-2" /></div></div>
          <div v-else-if="searchDone && searchResults.length === 0" class="text-center py-16 text-muted-foreground text-sm">未找到匹配结果</div>
          <div v-else-if="!searchDone" class="text-center py-16 text-muted-foreground text-sm">输入关键词开始检索知识库</div>
          <div v-else class="space-y-3">
            <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">找到 {{ searchResults.length }} 条</p>
            <div v-for="r in searchResults" :key="r.id" class="cursor-pointer rounded-md border border-border bg-background p-4 hover:border-primary/40 transition-colors" @click="openDetail(r)">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">[{{ typeLabel(r.type) }}]</span>
                  <span v-if="r.score != null" class="font-mono text-[10px] text-muted-foreground/70">相关度 {{ ((r.score||0)*100).toFixed(0) }}%</span>
                </div>
                <ChevronRight class="h-4 w-4 text-muted-foreground/40" />
              </div>
              <h3 class="font-display text-sm font-medium mt-2">{{ r.name || r.title }}</h3>
              <p class="text-xs text-muted-foreground mt-1 line-clamp-3 leading-relaxed">{{ r.snippet }}</p>
            </div>
          </div>
        </div>

        <!-- ==================== TAB 2: 管理知识 ==================== -->
        <div v-if="activeTab === 'manage'">
          <div class="flex items-center gap-x-5 gap-y-2 mb-5 flex-wrap">
            <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">类型</span>
            <button v-for="o in mgrTypes" :key="o.value"
              class="font-mono text-[10px] uppercase tracking-wider transition-colors"
              :class="mgrType === o.value ? 'text-primary' : 'text-muted-foreground/60 hover:text-foreground'"
              @click="mgrType = o.value">{{ o.label }}</button>
            <span class="flex-1" />
            <button class="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-accent transition-colors" @click="loadMgrList"><RefreshCw class="h-3 w-3" />刷新</button>
          </div>

          <div v-if="mgrLoading" class="space-y-3"><div v-for="i in 5" :key="i" class="rounded-md border border-border p-4"><Skeleton class="h-4 w-3/4" /></div></div>
          <div v-else-if="mgrEntries.length === 0" class="text-center py-12 border border-dashed border-border rounded-md text-muted-foreground text-sm">暂无条目,切换到「导入知识」添加</div>
          <div v-else class="divide-y divide-border border border-border rounded-md">
            <div v-for="e in mgrEntries" :key="e.id" class="flex items-center gap-3 bg-background px-4 py-3 hover:bg-accent/30 group transition-colors">
              <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground shrink-0">[{{ mgrTypeLabel }}]</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ e.name || e.title }}</p>
                <p class="font-mono text-[10px] text-muted-foreground/70 mt-0.5">{{ mgrSub(e) }}</p>
              </div>
              <div class="flex gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <button class="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground" title="编辑" @click="openEdit(e)"><Pencil class="h-3.5 w-3.5" /></button>
                <button class="rounded-md p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive" title="删除" @click="confirmDel(e)"><Trash2 class="h-3.5 w-3.5" /></button>
              </div>
            </div>
          </div>
          <p class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/70 text-center pt-3">共 {{ mgrEntries.length }} 条</p>
          <div class="mt-8 pt-6 border-t text-center">
            <button class="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground/50 hover:text-muted-foreground mx-auto transition-colors" :disabled="reindexing" @click="doReindex">
              <RefreshCw v-if="reindexing" class="h-3 w-3 animate-spin" /><Database v-else class="h-3 w-3" />{{ reindexing ? '重建中' : '重建向量索引' }}
            </button>
          </div>
        </div>

        <!-- ==================== TAB 3: 导入知识 ==================== -->
        <div v-if="activeTab === 'import'">
          <div class="rounded-lg border border-border bg-background p-6">
            <div class="flex items-center gap-x-5 gap-y-2 mb-5 flex-wrap">
              <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">类型</span>
              <button v-for="o in impTypes" :key="o.value"
                class="font-mono text-[10px] uppercase tracking-wider transition-colors"
                :class="impType === o.value ? 'text-primary' : 'text-muted-foreground/60 hover:text-foreground'"
                @click="impType = o.value">{{ o.label }}</button>
            </div>

            <!-- File drop zone -->
            <div class="relative rounded-md border border-dashed border-border p-6 text-center cursor-pointer transition-colors"
              :class="dragOver ? 'border-primary bg-primary/5' : impFile ? 'border-primary/50 bg-primary/5' : 'hover:border-muted-foreground/50'"
              @click="triggerFileInput" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="onDrop">
              <input ref="fileRef" type="file" accept=".txt,.md,.pdf,.doc,.docx,.tex" class="hidden" @change="onFileSel" />
              <template v-if="impFile">
                <div class="flex items-center justify-center gap-2 text-sm">
                  <FileText class="h-5 w-5 text-primary" /><span class="font-medium">{{ impFile.name }}</span>
                  <span class="font-mono text-[10px] text-muted-foreground">{{ fmtSize(impFile.size) }}</span>
                  <button class="ml-2 rounded-md p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive" @click.stop="clearFile"><X class="h-3.5 w-3.5" /></button>
                </div>
                <p class="font-mono text-[10px] text-muted-foreground/70 mt-1">文件内容已加载,可在下方编辑后提取</p>
              </template>
              <template v-else>
                <FileUp class="h-8 w-8 mx-auto text-muted-foreground/40 mb-2" />
                <p class="text-sm text-muted-foreground">拖拽文件到此处,或<span class="text-primary">点击选择</span></p>
                <p class="font-mono text-[10px] text-muted-foreground/60 mt-1">支持 .txt / .md / .pdf / .doc / .tex</p>
              </template>
            </div>

            <label class="block font-mono text-[10px] uppercase tracking-wider text-muted-foreground mb-2 mt-5">{{ impFile ? '文件内容(可编辑)' : '粘贴原始文本' }}</label>
            <textarea v-model="impText" rows="8" :placeholder="impPlaceholder"
              class="w-full resize-y rounded-md border border-border bg-background px-4 py-3 text-sm leading-relaxed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
            <div class="flex items-center gap-2 mt-3">
              <input v-model="impName" type="text" placeholder="名称(可选)" class="flex-1 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
              <button class="flex items-center rounded-md bg-foreground px-5 py-2.5 text-sm font-medium text-background hover:bg-foreground/90 disabled:opacity-50 transition-transform active:scale-[0.98]"
                :disabled="!impText.trim() || extracting" @click="doExtract">
                <Loader2 v-if="extracting" class="h-4 w-4 mr-1.5 animate-spin" /><Sparkles v-else class="h-4 w-4 mr-1.5" />{{ extracting ? '提取中' : 'LLM 提取并预览' }}
              </button>
            </div>
            <div v-if="extractError" class="mt-4 rounded-md border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">{{ extractError }}</div>
            <div v-if="extractPreview" class="mt-4">
              <p class="font-mono text-[10px] uppercase tracking-wider text-primary mb-2">提取完成</p>
              <pre class="rounded-md bg-zinc-950 p-4 font-mono text-xs text-zinc-300 overflow-auto max-h-96">{{ extractPreview }}</pre>
              <div class="flex gap-2 mt-3">
                <button class="flex items-center rounded-md bg-foreground px-5 py-2 text-sm font-medium text-background hover:bg-foreground/90 disabled:opacity-50 transition-transform active:scale-[0.98]"
                  :disabled="saving" @click="doSaveExtract"><Check v-if="!saving" class="h-4 w-4 mr-1" /><Loader2 v-else class="h-4 w-4 mr-1 animate-spin" />{{ saving ? '保存中' : '保存到知识库' }}</button>
                <button class="flex items-center rounded-md border border-border px-4 py-2 text-sm hover:bg-accent transition-colors" @click="extractPreview = ''; extractError = ''"><RotateCcw class="h-4 w-4 mr-1" />重新提取</button>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- Detail Dialog -->
    <Dialog :open="!!detailItem" @update:open="detailItem = null">
      <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader><DialogTitle class="font-display">{{ detailItem?.name || detailItem?.title }}</DialogTitle></DialogHeader>
        <div v-if="detailLoading" class="space-y-3"><Skeleton class="h-4 w-full" /><Skeleton class="h-4 w-5/6" /></div>
        <div v-else-if="detailData" class="text-sm space-y-4 py-2">
          <template v-if="detailData.type === 'method_card'">
            <p class="leading-relaxed">{{ (detailData.data as any).principle }}</p>
            <div><h4 class="font-display font-medium text-sm mb-1">适用条件</h4><ul class="list-disc list-inside text-muted-foreground text-sm"><li v-for="c in (detailData.data as any).applicable_when" :key="c">{{ c }}</li></ul></div>
          </template>
          <template v-if="detailData.type === 'paper'">
            <p class="leading-relaxed">{{ (detailData.data as any).model?.approach }}</p>
            <p class="text-muted-foreground leading-relaxed">{{ (detailData.data as any).evaluation?.lessons }}</p>
          </template>
          <template v-if="detailData.type === 'template'">
            <div v-for="s in (detailData.data as any).steps" :key="s.step" class="border-l-2 border-border pl-3 py-1">
              <h5 class="font-display font-medium text-sm">§{{ s.step }} {{ s.name }}</h5>
              <ul class="list-disc list-inside text-xs text-muted-foreground mt-1"><li v-for="c in s.checklist" :key="c">{{ c }}</li></ul>
            </div>
          </template>
        </div>
        <DialogFooter><DialogClose class="rounded-md border border-border px-4 py-2 text-sm hover:bg-accent transition-colors">关闭</DialogClose></DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Edit Dialog -->
    <Dialog :open="editOpen" @update:open="editOpen = $event">
      <DialogContent class="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader><DialogTitle class="font-display">编辑{{ mgrTypeLabel }}: {{ editForm.name || editForm.title }}</DialogTitle></DialogHeader>
        <div class="space-y-3 text-sm py-2">
          <p class="font-mono text-[10px] text-muted-foreground/70" v-if="editForm.id">ID: {{ editForm.id }}</p>
          <template v-if="mgrType === 'method'">
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">名称</label><input v-model="editForm.name" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">分类(逗号分隔)</label><input v-model="editForm.catStr" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">核心原理</label><textarea v-model="editForm.principle" rows="4" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">适用条件(每行一个)</label><textarea v-model="editForm.awStr" rows="3" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">典型场景(每行一个)</label><textarea v-model="editForm.tsStr" rows="3" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
          </template>
          <template v-if="mgrType === 'paper'">
            <div class="grid grid-cols-3 gap-2">
              <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">年份</label><input v-model.number="editForm.year" type="number" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
              <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">竞赛</label><input v-model="editForm.competition" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
              <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">题号</label><input v-model="editForm.problem_id" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            </div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">标题</label><input v-model="editForm.title" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">建模思路</label><textarea v-model="editForm.approach" rows="3" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">可学之处</label><textarea v-model="editForm.lessons" rows="2" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">评分 1-5</label><input v-model.number="editForm.quality_rating" type="number" min="1" max="5" class="w-20 rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
          </template>
          <template v-if="mgrType === 'template'">
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">名称</label><input v-model="editForm.name" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
            <div><label class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">适用类型(逗号分隔)</label><input v-model="editForm.atStr" class="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm mt-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
          </template>
        </div>
        <DialogFooter>
          <button class="rounded-md border border-border px-4 py-2 text-sm hover:bg-accent transition-colors" @click="editOpen = false">取消</button>
          <button class="rounded-md bg-foreground px-4 py-2 text-sm text-background hover:bg-foreground/90 disabled:opacity-50 transition-transform active:scale-[0.98]" :disabled="editSaving" @click="doEditSave">
            <Loader2 v-if="editSaving" class="h-4 w-4 mr-1 animate-spin" />{{ editSaving ? '保存中' : '保存' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirm -->
    <Dialog :open="delOpen" @update:open="delOpen = $event">
      <DialogContent class="max-w-sm">
        <DialogHeader><DialogTitle class="font-display">确认删除</DialogTitle><DialogDescription>确定删除 "{{ delTarget?.name || delTarget?.title }}"?不可撤销。</DialogDescription></DialogHeader>
        <DialogFooter>
          <button class="rounded-md border border-border px-4 py-2 text-sm hover:bg-accent transition-colors" @click="delOpen = false">取消</button>
          <button class="rounded-md bg-destructive px-4 py-2 text-sm text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50 transition-transform active:scale-[0.98]" :disabled="deleting" @click="doDelete">
            <Loader2 v-if="deleting" class="h-4 w-4 mr-1 animate-spin" />{{ deleting ? '删除中' : '确认删除' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  Search, Library, Loader2, ChevronRight, RefreshCw, Database,
  Upload, Sparkles, Check, RotateCcw, Pencil, Trash2, FileText, FileUp, X, Layers,
} from "lucide-vue-next";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog";
import {
  searchKB, getKBStats, reindexKB, getMethod, getPaper, getTemplate,
  listMethods, listPapers, listTemplates,
  uploadKnowledge, getExtractionJob,
  updateMethod, deleteMethod, updatePaper, deletePaper, updateTemplate, deleteTemplate,
  type SearchResult, type KBStats, type MethodCardSummary, type PaperSummary, type TemplateSummary,
} from "@/apis/knowledgeApi";

// ── tabs ─────────────────────────────────────────────────────────
const tabs = [
  { value: "search", label: "检索知识", icon: Search },
  { value: "manage", label: "管理知识", icon: Layers },
  { value: "import", label: "导入知识", icon: Upload },
];
const activeTab = ref("search");

// ── Tab 1: Search ───────────────────────────────────────────────
const searchQuery = ref(""); const searchFilter = ref(""); const searchProblem = ref("");
const searchLoading = ref(false); const searchDone = ref(false);
const searchResults = ref<SearchResult[]>([]);
const detailItem = ref<SearchResult | null>(null); const detailLoading = ref(false);
const detailData = ref<{ type: string; data: Record<string, unknown> } | null>(null);
const typeOpts = [{ label: "全部", value: "" }, { label: "方法卡片", value: "method_card" }, { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" }];
const probOpts = [{ label: "全部", value: "" }, { label: "优化", value: "optimization" }, { label: "预测", value: "prediction" }, { label: "评价", value: "evaluation" }, { label: "统计", value: "statistics" }];
function typeLabel(t: string) { return { method_card: "方法卡片", paper: "真题论文", template: "框架模板" }[t] || t; }
function badgeClass(t: string) { return { method_card: "bg-blue-100 text-blue-700", paper: "bg-purple-100 text-purple-700", template: "bg-green-100 text-green-700" }[t] || "bg-muted"; }
async function doSearch() {
  if (!searchQuery.value.trim()) return;
  searchLoading.value = true; searchDone.value = true;
  try { const r = await searchKB({ q: searchQuery.value.trim(), type: searchFilter.value || undefined, problem_type: searchProblem.value || undefined, k: 10 }); searchResults.value = r.data.results; }
  catch { searchResults.value = []; }
  finally { searchLoading.value = false; }
}
async function openDetail(r: SearchResult) {
  detailItem.value = r; detailLoading.value = true; detailData.value = null;
  try {
    if (r.type === "method_card") { const res = await getMethod(r.id); detailData.value = { type: "method_card", data: res.data as any }; }
    else if (r.type === "paper") { const res = await getPaper(r.id); detailData.value = { type: "paper", data: res.data as any }; }
    else { const res = await getTemplate(r.id); detailData.value = { type: "template", data: res.data as any }; }
  } catch { /* ignore */ }
  finally { detailLoading.value = false; }
}

// ── Tab 2: Manage ───────────────────────────────────────────────
const mgrType = ref("method"); const mgrEntries = ref<any[]>([]); const mgrLoading = ref(false);
const mgrTypes = [{ label: "方法卡片", value: "method" }, { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" }];
const mgrTypeLabel = computed(() => ({ method: "方法", paper: "论文", template: "模板" }[mgrType.value]));
const mgrBadgeClass = computed(() => ({ method: "bg-blue-100 text-blue-700", paper: "bg-purple-100 text-purple-700", template: "bg-green-100 text-green-700" }[mgrType.value]));
function mgrSub(e: any) {
  if (mgrType.value === "method") return (e.category || []).join(", ");
  if (mgrType.value === "paper") return `${e.year||""} ${e.competition||""} ${e.problem_id||""} ★${e.quality_rating||3}`;
  return `${e.steps_count||0} 个步骤`;
}
async function loadMgrList() {
  mgrLoading.value = true;
  try {
    if (mgrType.value === "method") { const r = await listMethods(); mgrEntries.value = r.data as any; }
    else if (mgrType.value === "paper") { const r = await listPapers(); mgrEntries.value = r.data as any; }
    else { const r = await listTemplates(); mgrEntries.value = r.data as any; }
  } catch { mgrEntries.value = []; }
  finally { mgrLoading.value = false; }
}
watch(mgrType, () => loadMgrList());

// Edit
const editOpen = ref(false); const editSaving = ref(false); const editForm = ref<Record<string, any>>({});
function openEdit(e: any) {
  editForm.value = { ...e };
  if (mgrType.value === "method") { editForm.value.catStr = (e.category||[]).join(", "); editForm.value.awStr = (e.applicable_when||[]).join("\n"); editForm.value.tsStr = (e.typical_scenarios||[]).join("\n"); }
  if (mgrType.value === "paper") { editForm.value.approach = e.model?.approach||""; editForm.value.lessons = e.evaluation?.lessons||""; }
  if (mgrType.value === "template") { editForm.value.atStr = (e.applicable_to||[]).join(", "); }
  editOpen.value = true;
}
async function doEditSave() {
  editSaving.value = true;
  try {
    const id = editForm.value.id; let data: any = { ...editForm.value };
    if (mgrType.value === "method") { data.category = (editForm.value.catStr||"").split(",").map((s:string)=>s.trim()).filter(Boolean); data.applicable_when = (editForm.value.awStr||"").split("\n").filter(Boolean); data.typical_scenarios = (editForm.value.tsStr||"").split("\n").filter(Boolean); delete data.catStr; delete data.awStr; delete data.tsStr; await updateMethod(id, data); }
    else if (mgrType.value === "paper") { data.model = { approach: editForm.value.approach||"", innovation: e.model?.innovation||"", solution_method: e.model?.solution_method||"" }; data.evaluation = { strengths: e.evaluation?.strengths||[], weaknesses: e.evaluation?.weaknesses||[], lessons: editForm.value.lessons||"" }; delete data.approach; delete data.lessons; await updatePaper(id, data); }
    else { data.applicable_to = (editForm.value.atStr||"").split(",").map((s:string)=>s.trim()).filter(Boolean); delete data.atStr; await updateTemplate(id, data); }
    editOpen.value = false; await loadMgrList(); await loadStats();
  } catch (e: any) { alert(`保存失败: ${e?.response?.data?.detail || e}`); }
  finally { editSaving.value = false; }
}

// Delete
const delOpen = ref(false); const delTarget = ref<any>(null); const deleting = ref(false);
function confirmDel(e: any) { delTarget.value = e; delOpen.value = true; }
async function doDelete() {
  deleting.value = true;
  try {
    const id = delTarget.value.id;
    if (mgrType.value === "method") await deleteMethod(id); else if (mgrType.value === "paper") await deletePaper(id); else await deleteTemplate(id);
    delOpen.value = false; delTarget.value = null; await loadMgrList(); await loadStats();
  } catch (e: any) { alert(`删除失败: ${e?.response?.data?.detail||e}`); }
  finally { deleting.value = false; }
}

// Reindex
const reindexing = ref(false);
async function doReindex() {
  reindexing.value = true;
  try { const r = await reindexKB(); alert(r.data.message); await loadStats(); }
  catch { alert("重建索引失败"); }
  finally { reindexing.value = false; }
}

// ── Tab 3: Import ───────────────────────────────────────────────
const impType = ref("method"); const impText = ref(""); const impName = ref(""); const impFile = ref<File | null>(null);
const dragOver = ref(false); const fileRef = ref<HTMLInputElement | null>(null);
const extracting = ref(false); const saving = ref(false); const extractPreview = ref(""); const extractError = ref("");
const impTypes = [{ label: "方法卡片", value: "method" }, { label: "真题论文", value: "paper" }, { label: "框架模板", value: "template" }];
const impPlaceholder = computed(() => ({
  method: "粘贴方法描述...\n例如: 粒子群优化算法(PSO)是一种基于群体智能的启发式优化算法...",
  paper: "粘贴论文内容...\n例如: 2024年国赛A题优秀论文...",
  template: "粘贴分析框架描述...\n例如: 第一步: 问题识别...",
}[impType.value]));

function triggerFileInput() { fileRef.value?.click(); }
function onFileSel(e: Event) { readFile((e.target as HTMLInputElement).files?.[0]); }
function onDrop(e: DragEvent) { dragOver.value = false; readFile(e.dataTransfer?.files?.[0]); }
function readFile(file?: File) {
  if (!file) return;
  if (file.size > 5*1024*1024) { extractError.value = "文件超过 5MB"; return; }
  impFile.value = file; if (!impName.value) impName.value = file.name.replace(/\.[^.]+$/, "");
  const r = new FileReader(); r.onload = () => { impText.value = r.result as string; }; r.readAsText(file);
}
function clearFile() { impFile.value = null; impText.value = ""; if (fileRef.value) fileRef.value.value = ""; }
function fmtSize(b: number) { if (b<1024) return `${b}B`; if (b<1048576) return `${(b/1024).toFixed(1)}KB`; return `${(b/1048576).toFixed(1)}MB`; }

async function doExtract() {
  if (!impText.value.trim()) return;
  extracting.value = true; extractError.value = ""; extractPreview.value = "";
  try {
    const res = await uploadKnowledge({ text: impText.value.trim(), file: impFile.value || undefined, kb_type: impType.value, name: impName.value });
    let tries = 0;
    while (tries < 60) {
      await new Promise(r => setTimeout(r, 1000));
      const job = await getExtractionJob(res.data.job_id);
      if (job.data.status === "completed") { extractPreview.value = job.data.result?.yaml_content || ""; break; }
      if (job.data.status === "error") { extractError.value = job.data.error || "提取失败"; break; }
      tries++;
    }
    if (tries >= 60) extractError.value = "提取超时";
  } catch (e: any) { extractError.value = `请求失败: ${e?.response?.data?.detail || e}`; }
  finally { extracting.value = false; }
}
async function doSaveExtract() {
  saving.value = true; await loadStats(); await new Promise(r => setTimeout(r, 500));
  extractPreview.value = ""; extractError.value = ""; impText.value = ""; impName.value = ""; clearFile(); saving.value = false;
  alert("已保存到知识库,切换到「检索知识」可搜索验证。");
}

// ── shared ──────────────────────────────────────────────────────
const stats = ref<KBStats>({ methods_count:0,papers_count:0,templates_count:0,total:0 });
async function loadStats() { try { const r = await getKBStats(); stats.value = r.data; } catch {/*ignore*/} }
onMounted(() => loadStats());
</script>
