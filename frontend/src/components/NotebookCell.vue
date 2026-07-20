<template>
  <div class="rounded-sm border border-border overflow-hidden bg-background">
    <!-- Cell Header:等宽小标 + 细线 -->
    <div class="flex items-center justify-between px-3 py-1.5 border-b border-border bg-muted/20">
      <div class="flex items-center gap-2">
        <span class="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          {{ cellTypeLabel }}<template v-if="executionCount !== undefined">[{{ executionCount }}]</template>
        </span>
      </div>
      <button
        v-if="cell_type === 'code'"
        class="flex items-center gap-1 rounded-sm px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
        title="运行"
        @click="emit('run')"
      >
        <Play class="h-3 w-3" />
        <span>运行</span>
      </button>
    </div>

    <!-- Cell Content -->
    <div class="p-3">
      <!-- Code cell -->
      <pre
        v-if="cell_type === 'code'"
        class="text-xs font-mono overflow-x-auto leading-relaxed"
        v-html="highlightedCode"
      />

      <!-- Markdown cell -->
      <div
        v-else-if="cell_type === 'markdown'"
        class="prose prose-sm dark:prose-invert max-w-none"
        v-html="renderedMarkdown"
      />

      <!-- Raw cell -->
      <pre v-else class="text-xs font-mono whitespace-pre-wrap text-muted-foreground">{{ source }}</pre>
    </div>

    <!-- Outputs:细线分隔,等宽 -->
    <div v-if="outputs && outputs.length > 0" class="border-t border-border bg-muted/10">
      <div
        v-for="(output, idx) in outputs"
        :key="idx"
        class="border-b border-border last:border-b-0"
      >
        <!-- Text output -->
        <pre
          v-if="output.type === 'text' || output.type === 'stream'"
          class="text-xs p-3 whitespace-pre-wrap font-mono max-h-60 overflow-y-auto leading-relaxed"
        >{{ output.text ?? output.content }}</pre>

        <!-- Image output -->
        <div v-else-if="output.type === 'image' || output.type === 'display_data'" class="p-3 flex justify-center">
          <img
            v-if="output.data?.image_png || output.url"
            :src="output.url || `data:image/png;base64,${output.data?.image_png}`"
            class="max-w-full rounded-sm border border-border"
            :alt="output.alt ?? '输出图片'"
          />
        </div>

        <!-- LaTeX output -->
        <div
          v-else-if="output.type === 'latex'"
          class="p-3 text-sm"
          v-html="renderLatex(output.content ?? output.text ?? '')"
        />

        <!-- Table output:细线表格 -->
        <div v-else-if="output.type === 'table'" class="p-3 overflow-x-auto">
          <table class="text-xs border-collapse">
            <thead>
              <tr>
                <th
                  v-for="(h, hi) in (output.headers ?? [])"
                  :key="hi"
                  class="border border-border px-2 py-1 font-mono font-medium text-left text-muted-foreground uppercase tracking-wider text-[10px]"
                >{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in (output.rows ?? [])" :key="ri">
                <td
                  v-for="(cell, ci) in row"
                  :key="ci"
                  class="border border-border px-2 py-1 font-mono tabular-nums"
                >{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Error output:暖橙边框(去红底红字) -->
        <pre
          v-else-if="output.type === 'error'"
          class="text-xs p-3 whitespace-pre-wrap font-mono text-destructive border-l-2 border-destructive/40 bg-destructive/5 leading-relaxed"
        >{{ output.text ?? output.traceback?.join("\n") }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Play } from "lucide-vue-next";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";

marked.use(markedKatex({ throwOnError: false, nonStandard: true }));

const props = defineProps<{
  cell_type: "code" | "markdown" | "raw";
  source?: string;
  executionCount?: number;
  outputs?: Array<Record<string, unknown>>;
}>();

const emit = defineEmits<{
  run: [];
}>();

const cellTypeLabel = computed(() => {
  switch (props.cell_type) {
    case "code": return "code";
    case "markdown": return "md";
    default: return "raw";
  }
});

const highlightedCode = computed(() => {
  if (!props.source) return "";
  return escapeHtml(props.source);
});

const renderedMarkdown = computed(() => {
  if (!props.source) return "";
  return marked.parse(props.source) as string;
});

function renderLatex(content: string): string {
  return marked.parse(`$$${content}$$`) as string;
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
</script>
