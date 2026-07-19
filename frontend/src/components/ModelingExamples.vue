<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold">经典例题</h3>
      <SearchForm
        :categories="categories"
        placeholder="搜索例题..."
        @search="onSearch"
        @filter-change="onFilterChange"
      />
    </div>

    <!-- Category tabs -->
    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors"
        :class="activeFilter === tab.value
          ? 'bg-primary text-primary-foreground'
          : 'bg-muted text-muted-foreground hover:bg-accent'"
        @click="activeFilter = tab.value; $emit('filter', tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Examples grid -->
    <div class="grid gap-3 sm:grid-cols-2">
      <div
        v-for="example in filteredExamples"
        :key="example.id"
        class="group cursor-pointer rounded-xl border bg-card p-4 transition-all hover:shadow-md hover:border-primary/30"
        @click="$router.push(`/example/${example.id}`)"
      >
        <div class="flex items-start justify-between gap-2">
          <h4 class="font-medium text-sm group-hover:text-primary transition-colors line-clamp-2">
            {{ example.title }}
          </h4>
        </div>

        <div class="flex items-center gap-2 mt-2">
          <span class="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
            {{ example.category }}
          </span>
          <span
            class="inline-flex items-center rounded-full px-2 py-0.5 text-xs"
            :class="difficultyClass(example.difficulty)"
          >
            {{ example.difficulty }}
          </span>
        </div>

        <p class="text-xs text-muted-foreground mt-2 line-clamp-2">
          {{ example.description }}
        </p>

        <div class="flex items-center gap-1 mt-3 text-xs text-muted-foreground">
          <BookOpen class="h-3 w-3" />
          <span>{{ example.competition }}</span>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div
      v-if="filteredExamples.length === 0"
      class="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center"
    >
      <Search class="h-8 w-8 text-muted-foreground/50 mb-2" />
      <p class="text-sm text-muted-foreground">未找到匹配的例题</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { BookOpen, Search } from "lucide-vue-next";
import SearchForm from "@/components/SearchForm.vue";

interface Example {
  id: number;
  title: string;
  category: string;
  difficulty: string;
  description: string;
  competition: string;
}

defineProps<{
  examples: Example[];
}>();

defineEmits<{
  filter: [category: string];
}>();

const categories = [
  { label: "优化问题", value: "optimization" },
  { label: "预测问题", value: "prediction" },
  { label: "评价问题", value: "evaluation" },
  { label: "图论问题", value: "graph" },
  { label: "微分方程", value: "differential" },
];

const tabs = [
  { label: "全部", value: "" },
  { label: "优化", value: "optimization" },
  { label: "预测", value: "prediction" },
  { label: "评价", value: "evaluation" },
  { label: "图论", value: "graph" },
];

const activeFilter = ref("");
const searchQuery = ref("");
const filterCategory = ref("");

const filteredExamples = computed(() => {
  // In a real implementation, filtering would be done against the examples prop
  return [];
});

function onSearch(query: string) {
  searchQuery.value = query;
}

function onFilterChange(cat: string) {
  filterCategory.value = cat;
}

function difficultyClass(difficulty: string): string {
  switch (difficulty) {
    case "简单":
      return "bg-green-100 text-green-700";
    case "中等":
      return "bg-yellow-100 text-yellow-700";
    case "困难":
      return "bg-red-100 text-red-700";
    default:
      return "bg-muted text-muted-foreground";
  }
}
</script>
