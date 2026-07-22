/** 项目统一的 Tailwind 样式常量。
 *
 * 所有按钮、交互元素从此引入，禁止在各页面模板中硬编码重复类名。
 */

// ── 缩放动画 ──
/* 两段式：悬停 → 2%，按下 → 3% */
export const SCALE_PRESS =
  "transition-transform hover:scale-[0.98] active:scale-[0.97]";

// ── 按钮 ──
/* 主按钮（实心 + focus ring） — 首页 CTA */
export const BTN_PRIMARY = [
  "group inline-flex items-center gap-2 rounded-md",
  "bg-foreground px-5 py-2.5 text-sm font-medium text-background",
  SCALE_PRESS,
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
].join(" ");

/* 主按钮（紧凑，无 focus ring） — 弹框保存 */
export const BTN_PRIMARY_COMPACT = [
  "rounded-md bg-foreground px-4 py-2 text-sm text-background",
  "hover:bg-foreground/90 disabled:opacity-50",
  SCALE_PRESS,
].join(" ");

/* 破坏性按钮 */
export const BTN_DANGER = [
  "rounded-md bg-destructive px-4 py-2 text-sm text-destructive-foreground",
  "hover:bg-destructive/90 disabled:opacity-50",
  SCALE_PRESS,
].join(" ");

// ── 导航 ──
export const NAV_ITEM = [
  "group relative flex w-full items-center gap-3 py-2 pr-4 pl-5 text-sm",
  SCALE_PRESS,
].join(" ");

// ── 布局 ──
export const SECTION_LABEL =
  "font-mono text-[10px] uppercase tracking-wider text-muted-foreground";
