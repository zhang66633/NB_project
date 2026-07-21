<template>
  <div class="flex h-full bg-background">
    <div class="flex-1 min-w-0 relative">
      <ChatArea
        :messages="chatSession.activeTeachMessages"
        :is-running="chatSession.isRunning"
        empty-text="开始学习"
        empty-subtext="描述你的问题，我将引导你逐步建立建模思维"
        input-placeholder="描述你想学习的建模问题..."
        @send="handleUserSend"
      />
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
  "🤔 **让我们一起来分析这个问题。**\n\n首先，你能尝试回答：这个问题的**核心目标**是什么？是最大化某个量，还是最小化？",
  "📝 **很好！下一步我们来看决策变量。**\n\n在这个问题中，哪些因素的值是我们可以决定的？试着列出 2-3 个关键变量。",
  "💡 **现在考虑约束条件。**\n\n我们的决策受到哪些现实条件的限制？试着至少列出 3 条约束。",
  "✅ **非常好！现在我们来建立目标函数。**\n\n基于你的分析，目标函数应该是什么样的？用数学表达式描述一下。",
];

let replyIndex = 0;

function generateId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function handleUserSend(text: string) {
  let sessionId = chatSession.activeTeachId;

  if (!sessionId) {
    sessionId = chatSession.createSession("teach");
  }

  const userMsg: Message = {
    id: generateId(),
    msg_type: "user",
    content: text,
    created_at: new Date().toISOString(),
  };
  chatSession.addMessage("teach", sessionId, userMsg);

  chatSession.isRunning = true;

  const existingMessages = chatSession.activeTeachMessages;
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
    chatSession.addMessage("teach", sessionId, reply);
    chatSession.isRunning = false;
    replyIndex++;
  }, 1000);
}

onMounted(() => {
  if (!chatSession.activeTeachId && chatSession.sortedTeachSessions.length > 0) {
    chatSession.switchSession("teach", chatSession.sortedTeachSessions[0].id);
  }
});
</script>
