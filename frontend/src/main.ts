import { createPinia } from "pinia";
import { createApp } from "vue";
import "katex/dist/katex.min.css";
import "@/assets/style.css";
import App from "@/App.vue";
import router from "@/router";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import { useAuthStore } from "@/stores/auth";

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
const app = createApp(App);

app.use(router);
app.use(pinia);

// 启动时检查已有 token 是否有效
const auth = useAuthStore();
auth.checkSession();

app.mount("#app");
