/** 归档 Store — 已归档的方案和教学笔记，localStorage 持久化 */
import { ref, computed } from "vue";
import { defineStore } from "pinia";
import type { Message } from "@/types/response";

/** 归档条目类型 */
export type ArchiveKind = "solution" | "teaching";

/** 归档条目 */
export interface ArchiveItem {
  id: string;
  title: string;
  kind: ArchiveKind;
  /** 归档来源: "selection" 选中消息 / "session" 整个会话 */
  source: "selection" | "session";
  /** 归档时原始会话的模式 */
  mode: "teach" | "execute" | "chat";
  /** 被归档的消息列表 */
  messages: Message[];
  /** 用户备注 */
  note?: string;
  createdAt: string;
  updatedAt: string;
}

function now() {
  return new Date().toISOString();
}

function genId() {
  return `arch_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useArchiveStore = defineStore(
  "archive",
  () => {
    const items = ref<ArchiveItem[]>([]);

    /** 按更新时间倒序排列 */
    const sortedItems = computed(() =>
      [...items.value].sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
      ),
    );

    /** 方案归档列表 */
    const solutionItems = computed(() =>
      sortedItems.value.filter((i) => i.kind === "solution"),
    );

    /** 教学笔记归档列表 */
    const teachingItems = computed(() =>
      sortedItems.value.filter((i) => i.kind === "teaching"),
    );

    /** 根据 ID 获取归档详情 */
    function getById(id: string): ArchiveItem | undefined {
      return items.value.find((i) => i.id === id);
    }

    /** 创建归档 — 从选中消息 */
    function createFromMessages(
      title: string,
      kind: ArchiveKind,
      messages: Message[],
      mode: "teach" | "execute" | "chat",
      note?: string,
    ): string {
      const id = genId();
      items.value.push({
        id,
        title: title.trim() || "未命名归档",
        kind,
        source: "selection",
        mode,
        messages: [...messages],
        note,
        createdAt: now(),
        updatedAt: now(),
      });
      return id;
    }

    /** 创建归档 — 从整个会话 */
    function createFromSession(
      title: string,
      kind: ArchiveKind,
      sessionMessages: Message[],
      mode: "teach" | "execute" | "chat",
      note?: string,
    ): string {
      const id = genId();
      items.value.push({
        id,
        title: title.trim() || "未命名归档",
        kind,
        source: "session",
        mode,
        messages: [...sessionMessages],
        note,
        createdAt: now(),
        updatedAt: now(),
      });
      return id;
    }

    /** 删除归档 */
    function deleteArchive(id: string) {
      const idx = items.value.findIndex((i) => i.id === id);
      if (idx !== -1) items.value.splice(idx, 1);
    }

    /** 更新归档标题 */
    function renameArchive(id: string, newTitle: string) {
      const item = items.value.find((i) => i.id === id);
      if (item) {
        item.title = newTitle.trim() || "未命名归档";
        item.updatedAt = now();
      }
    }

    /** 更新归档备注 */
    function updateNote(id: string, note: string) {
      const item = items.value.find((i) => i.id === id);
      if (item) {
        item.note = note;
        item.updatedAt = now();
      }
    }

    return {
      items, sortedItems, solutionItems, teachingItems,
      getById, createFromMessages, createFromSession,
      deleteArchive, renameArchive, updateNote,
    };
  },
  {
    persist: {
      key: "mma-archives",
      storage: localStorage,
      pick: ["items"],
    },
  },
);
