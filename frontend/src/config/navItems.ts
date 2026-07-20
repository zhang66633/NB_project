import { Home, MessageSquare, FolderOpen, Library, BookOpen } from "lucide-vue-next";

export interface NavItem {
  label: string;
  path: string;
  icon: typeof Home;
}

/** 侧栏与移动抽屉共用的导航配置 */
export const navItems: NavItem[] = [
  { label: "首页", path: "/", icon: Home },
  { label: "对话", path: "/chat", icon: MessageSquare },
  { label: "任务", path: "/task/0", icon: FolderOpen },
  { label: "知识库", path: "/knowledge", icon: Library },
  { label: "例题", path: "/example/1", icon: BookOpen },
];
