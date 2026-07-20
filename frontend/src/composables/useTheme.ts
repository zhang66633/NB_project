import { ref, watch, onMounted } from "vue";

export type Theme = "light" | "dark";

const STORAGE_KEY = "theme";

// 全局单例状态(跨组件共享)
const theme = ref<Theme>("light");
let initialized = false;

function applyTheme(t: Theme) {
  const root = document.documentElement;
  if (t === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

function init() {
  if (initialized) return;
  initialized = true;

  // 读取已应用的状态(index.html 防闪烁脚本已先设过 class)
  const isDark = document.documentElement.classList.contains("dark");
  theme.value = isDark ? "dark" : "light";

  // 持久化监听
  watch(theme, (t) => {
    applyTheme(t);
    try {
      localStorage.setItem(STORAGE_KEY, t);
    } catch (e) {
      /* localStorage 不可用时忽略 */
    }
  });
}

export function useTheme() {
  onMounted(init);

  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
  }

  function setTheme(t: Theme) {
    theme.value = t;
  }

  return { theme, toggle, setTheme };
}
