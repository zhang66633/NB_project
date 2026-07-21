import { Home, MessageSquare, GraduationCap, FileText, Library, BookOpen } from "lucide-vue-next";

export interface NavItem {
  label: string;
  path: string;
  icon: typeof Home;
}

export const navItems: NavItem[] = [
  { label: "首页", path: "/", icon: Home },
  { label: "对话", path: "/chat", icon: MessageSquare },
  { label: "教学", path: "/teach", icon: GraduationCap },
  { label: "方案", path: "/solution", icon: FileText },
  { label: "知识库", path: "/knowledge", icon: Library },
  { label: "例题", path: "/example/1", icon: BookOpen },
];
