<template>
  <div class="flex h-full bg-background">
    <div class="flex-1 min-w-0 relative">
      <ChatArea :messages="chatSession.activeChatMessages" @send="handleUserSend" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import ChatArea from "@/components/ChatArea.vue";
import { useChatSessionStore } from "@/stores/chatSession";
import type { Message } from "@/utils/response";

const chatSession = useChatSessionStore();

const mockReplies = [
  "你好！我是数学建模助手。有什么我可以帮你的吗？",
  "这是一个很好的问题。让我想想...",
  "数学建模中有很多经典问题，比如运输问题、指派问题、TSP等。你想了解哪一个？",
  "随时可以继续讨论！",
];

let replyIndex = 0;

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function handleUserSend(text: string) {
  let sessionId = chatSession.activeChatId;

  if (!sessionId) {
    sessionId = chatSession.createSession("chat");
  }

  const userMsg: Message = {
    id: generateId(),
    msg_type: "user",
    content: text,
    created_at: new Date().toISOString(),
  };
  chatSession.addMessage("chat", sessionId, userMsg);

  chatSession.isRunning = true;

  const existingMessages = chatSession.activeChatMessages;
  const hasAgentReply = existingMessages.some((m) => m.msg_type === "agent");
  if (hasAgentReply && existingMessages[existingMessages.length - 1].msg_type !== "user") {
    chatSession.isRunning = false;
    return;
  }

  setTimeout(() => {
    const reply: Message = {
      id: generateId(),
      msg_type: "agent",
      content: mockReplies[replyIndex % mockReplies.length],
      created_at: new Date().toISOString(),
    };
    chatSession.addMessage("chat", sessionId, reply);
    chatSession.isRunning = false;
    replyIndex++;
  }, 800);
}

onMounted(() => {
  if (!chatSession.activeChatId && chatSession.sortedChatSessions.length > 0) {
    chatSession.switchSession("chat", chatSession.sortedChatSessions[0].id);
  }
});
</script>
