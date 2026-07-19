<template>
  <div class="flex h-screen bg-background">
    <AppSidebar />
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Library class="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
        <p class="text-muted-foreground text-sm">知识库 — 进入对话后可用</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Library } from "lucide-vue-next";
import AppSidebar from "@/components/AppSidebar.vue";
</script>
