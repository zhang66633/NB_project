<template>
  <div class="flex items-center gap-2">
    <div class="relative flex-1">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <input
        v-model="query"
        type="text"
        :placeholder="placeholder"
        class="flex h-10 w-full rounded-lg border border-input bg-background pl-9 pr-4 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        @input="emit('search', query)"
        @keydown.enter="emit('search', query)"
      />
      <button
        v-if="query"
        class="absolute right-2 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground hover:text-foreground"
        @click="clearSearch"
      >
        <X class="h-4 w-4" />
      </button>
    </div>
    <select
      v-if="categories.length > 0"
      v-model="selectedCategory"
      class="h-10 rounded-lg border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      @change="emit('filter-change', selectedCategory)"
    >
      <option value="">全部分类</option>
      <option v-for="cat in categories" :key="cat.value" :value="cat.value">
        {{ cat.label }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Search, X } from "lucide-vue-next";

const props = withDefaults(defineProps<{
  placeholder?: string;
  categories?: { label: string; value: string }[];
}>(), {
  placeholder: "搜索...",
  categories: () => [],
});

const emit = defineEmits<{
  search: [query: string];
  "filter-change": [category: string];
}>();

const query = ref("");
const selectedCategory = ref("");

function clearSearch() {
  query.value = "";
  emit("search", "");
}
</script>
