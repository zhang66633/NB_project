<template>
  <div class="flex h-full flex-col overflow-hidden">
    <header class="flex items-center justify-between border-b px-6 py-4 shrink-0">
      <div class="flex items-center gap-3">
        <Button variant="ghost" size="icon" @click="router.back()">
          <ArrowLeft class="h-4 w-4" />
        </Button>
        <div>
          <h1 class="text-lg font-semibold">API Keys</h1>
          <p class="text-xs text-muted-foreground">管理用于调用大模型的 API 凭证</p>
        </div>
      </div>
      <Button @click="showAdd = true">
        <Plus class="h-4 w-4 mr-1" />
        添加 Key
      </Button>
    </header>

    <div class="flex-1 overflow-y-auto overflow-x-hidden p-6">
      <div v-if="loading" class="flex items-center justify-center py-12 text-sm text-muted-foreground">
        <Loader2 class="h-4 w-4 mr-2 animate-spin" /> 加载中...
      </div>

      <div v-else-if="keys.length === 0" class="rounded-lg border border-dashed p-12 text-center">
        <Key class="h-10 w-10 mx-auto text-muted-foreground/50" />
        <p class="mt-4 text-sm text-muted-foreground">还没有 API Key</p>
        <p class="mt-1 text-xs text-muted-foreground">添加后可以在对话/任务中使用对应模型</p>
      </div>

      <div v-else class="grid gap-3 max-w-3xl">
        <div
          v-for="k in keys"
          :key="k.id"
          class="flex items-center justify-between rounded-lg border p-4 hover:bg-accent/30 transition-colors"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div class="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 shrink-0">
              <Key class="h-4 w-4 text-primary" />
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <p class="font-medium truncate">{{ k.name }}</p>
                <span v-if="k.is_default" class="text-[10px] font-mono uppercase bg-primary/10 text-primary px-1.5 py-0.5 rounded">默认</span>
              </div>
              <p class="text-xs text-muted-foreground font-mono">{{ k.masked_key }} · {{ k.provider }} · {{ k.model_name }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <Button v-if="!k.is_default" variant="outline" size="sm" @click="handleSetDefault(k.id)">
              <Check class="h-3 w-3 mr-1" />
              设为默认
            </Button>
            <Button variant="ghost" size="icon" class="text-destructive hover:text-destructive" @click="handleDelete(k.id)">
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAdd" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showAdd = false">
      <div class="w-full max-w-md rounded-lg border bg-background p-6 shadow-xl">
        <h2 class="text-lg font-semibold mb-4">添加 API Key</h2>
        <div class="space-y-3">
          <div>
            <label class="text-sm font-medium">名称</label>
            <Input v-model="form.name" placeholder="例如: 我的 DeepSeek" class="mt-1" />
          </div>
          <div>
            <label class="text-sm font-medium">服务商</label>
            <select v-model="form.provider" class="mt-1 w-full h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="openai">OpenAI / DeepSeek / 兼容 OpenAI 协议</option>
              <option value="anthropic">Anthropic (Claude)</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium">模型名称</label>
            <Input v-model="form.model_name" placeholder="deepseek-chat" class="mt-1" />
          </div>
          <div>
            <label class="text-sm font-medium">Key</label>
            <Input v-model="form.key" type="password" placeholder="sk-..." class="mt-1" />
          </div>
        </div>
        <div class="mt-5 flex justify-end gap-2">
          <Button variant="ghost" @click="showAdd = false">取消</Button>
          <Button :disabled="!form.name || !form.key || !form.model_name || saving" @click="handleAdd">
            <Loader2 v-if="saving" class="h-4 w-4 mr-1 animate-spin" />
            保存
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Key, Plus, Trash2, Loader2, Check } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getApiKeys, addApiKey, deleteApiKey, setDefaultApiKey } from "@/apis/apiKeyApi";

interface ApiKeyItem {
  id: string;
  name: string;
  provider: string;
  model_name: string;
  masked_key: string;
  is_default: boolean;
}

const router = useRouter();
const keys = ref<ApiKeyItem[]>([]);
const loading = ref(false);
const saving = ref(false);
const showAdd = ref(false);
const form = ref({ name: "", provider: "openai", model_name: "deepseek-chat", key: "" });

async function load() {
  loading.value = true;
  try {
    const r: any = await getApiKeys();
    keys.value = r.data || r || [];
  } catch (e) {
    console.error(e);
    keys.value = [];
  } finally {
    loading.value = false;
  }
}

async function handleAdd() {
  saving.value = true;
  try {
    await addApiKey(form.value);
    showAdd.value = false;
    form.value = { name: "", provider: "openai", model_name: "deepseek-chat", key: "" };
    await load();
  } catch (e) {
    console.error(e);
  } finally {
    saving.value = false;
  }
}

async function handleDelete(id: string) {
  try {
    await deleteApiKey(id);
    await load();
  } catch (e) {
    console.error(e);
  }
}

async function handleSetDefault(id: string) {
  try {
    await setDefaultApiKey(id);
    await load();
  } catch (e) {
    console.error(e);
  }
}

onMounted(load);
</script>