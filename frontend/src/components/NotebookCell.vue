<template>
  <div class="border rounded-lg overflow-hidden">
    <!-- Cell Header -->
    <div class="flex items-center justify-between bg-muted/50 px-3 py-1.5 border-b">
      <div class="flex items-center gap-2">
        <span class="text-xs font-mono text-muted-foreground">
          {{ cellTypeLabel }}
          <template v-if="executionCount !== undefined">[{{ executionCount }}]</template>
        </span>
      </div>
      <div class="flex items-center gap-1">
        <button
          v-if="cell_type === 'code'"
          class="flex items-center gap-1 rounded px-2 py-0.5 text-xs hover:bg-accent transition-colors"
          title="运行"
        >
          <Play class="h-3 w-3" />
          <span>运行</span>
        </button>
      </div>
    </div>

    <!-- Cell Content -->
    <div class="p-3">
      <!-- Code cell - source -->
      <pre
        v-if="cell_type === 'code'"
        class="text-sm font-mono overflow-x-auto"
        v-html="highlightedCode"
      />

      <!-- Markdown cell -->
      <div
        v-else-if="cell_type === 'markdown'"
        class="prose prose-sm dark:prose-invert max-w-none"
        v-html="renderedMarkdown"
      />

      <!-- Raw cell -->
      <pre v-else class="text-sm whitespace-pre-wrap">{{ source }}</pre>
    </div>

    <!-- Outputs -->
    <div v-if="outputs && outputs.length > 0" class="border-t bg-muted/20">
      <div
        v-for="(output, idx) in outputs"
        :key="idx"
        class="border-b last:border-b-0"
      >
        <!-- Text output -->
        <pre
          v-if="output.type === 'text' || output.type === 'stream'"
          class="text-xs p-3 whitespace-pre-wrap font-mono max-h-60 overflow-y-auto"
        >{{ output.text ?? output.content }}</pre>

        <!-- Image output -->
        <div v-else-if="output.type === 'image' || output.type === 'display_data'" class="p-3 flex justify-center">
          <img
            v-if="output.data?.image_png || output.url"
            :src="output.url || `data:image/png;base64,${output.data?.image_png}`"
            class="max-w-full rounded"
            :alt="output.alt ?? '输出图片'"
          />
        </div>

        <!-- LaTeX output -->
        <div
          v-else-if="output.type === 'latex'"
          class="p-3 text-sm"
          v-html="renderLatex(output.content ?? output.text ?? '')"
        />

        <!-- Table output -->
        <div v-else-if="output.type === 'table'" class="p-3 overflow-x-auto">
          <table class="text-xs border-collapse">
            <thead>
              <tr>
                <th
                  v-for="(h, hi) in (output.headers ?? [])"
                  :key="hi"
                  class="border px-2 py-1 bg-muted font-medium text-left"
                >{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in (output.rows ?? [])" :key="ri">
                <td
                  v-for="(cell, ci) in row"
                  :key="ci"
                  class="border px-2 py-1"
                >{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Error output -->
        <pre
          v-else-if="output.type === 'error'"
          class="text-xs p-3 whitespace-pre-wrap font-mono text-red-600 bg-red-50 dark:bg-red-950/20"
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

marked.use(markedKatex({ throwOnError: false }));

const props = defineProps<{
  cell_type: "code" | "markdown" | "raw";
  source?: string;
  executionCount?: number;
  outputs?: Array<Record<string, unknown>>;
}>();

const cellTypeLabel = computed(() => {
  switch (props.cell_type) {
    case "code": return "代码";
    case "markdown": return "Markdown";
    default: return "Raw";
  }
});

const highlightedCode = computed(() => {
  if (!props.source) return "";
  // Simple escaping for display; highlight.js would be used here in production
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
