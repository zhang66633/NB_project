import type { ModelConfig } from "@/utils/interface";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useApiKeysStore = defineStore("apiKeys", () => {
  const configs = ref<Record<string, ModelConfig>>({});

  function setConfig(agentType: string, config: ModelConfig) {
    configs.value[agentType] = config;
  }

  function getConfig(agentType: string): ModelConfig | undefined {
    return configs.value[agentType];
  }

  return { configs, setConfig, getConfig };
});
