<template>
  <div class="space-y-4">
    <div>
      <h3 class="text-base font-semibold">验证分析智能体</h3>
      <p class="text-sm text-muted-foreground mt-1">负责模型验证与鲁棒性分析</p>
    </div>

    <div class="space-y-3">
      <div class="space-y-1.5">
        <label class="text-sm font-medium">API Key</label>
        <input
          v-model="config.apiKey"
          type="password"
          placeholder="sk-..."
          class="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>
      <div class="space-y-1.5">
        <label class="text-sm font-medium">Base URL</label>
        <input
          v-model="config.baseUrl"
          type="text"
          placeholder="https://api.openai.com/v1"
          class="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>
      <div class="space-y-1.5">
        <label class="text-sm font-medium">模型 ID</label>
        <input
          v-model="config.modelId"
          type="text"
          placeholder="gpt-4o"
          class="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>
      <div class="space-y-1.5">
        <label class="text-sm font-medium">API 类型</label>
        <select
          v-model="config.apiType"
          class="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <option value="openai-chat">OpenAI Chat</option>
          <option value="openai-responses">OpenAI Responses</option>
          <option value="anthropic">Anthropic</option>
        </select>
      </div>
      <div class="space-y-1.5">
        <label class="text-sm font-medium">上下文窗口 (可选)</label>
        <input
          v-model.number="config.contextWindow"
          type="number"
          placeholder="128000"
          class="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
      </div>
    </div>

    <div class="flex justify-end">
      <button
        class="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        @click="save"
      >
        <Save class="h-4 w-4 mr-1.5" />
        保存配置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";
import { Save } from "lucide-vue-next";
import { useApiKeysStore } from "@/stores/apiKeys";
import { AgentType } from "@/utils/enum";
import type { ModelConfig } from "@/utils/interface";

const store = useApiKeysStore();

const config = reactive<ModelConfig>({
  apiKey: "",
  baseUrl: "",
  modelId: "",
  apiType: "openai-chat",
  contextWindow: undefined,
});

onMounted(() => {
  const saved = store.getConfig(AgentType.VERIFICATION);
  if (saved) {
    Object.assign(config, saved);
  }
});

function save() {
  store.setConfig(AgentType.VERIFICATION, { ...config });
}
</script>
