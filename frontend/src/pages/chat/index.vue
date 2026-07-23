<template>
  <div class="flex h-full bg-background">
    <div class="flex-1 min-w-0 relative">
      <ChatArea
        :messages="chatSession.activeChatMessages"
        :is-running="chatSession.getIsRunning('chat')"
        @send="handleUserSend"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import ChatArea from "@/components/ChatArea.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import { useStreamChat } from "@/composables/useStreamChat";

const chatSession = useChatSessionStore();
const { handleUserSend, restoreLatestSession } = useStreamChat("chat", "chat");

onMounted(restoreLatestSession);
</script>
