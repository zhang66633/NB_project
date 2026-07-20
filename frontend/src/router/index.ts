import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import AppLayout from "@/components/AppLayout.vue";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    component: () => import("@/pages/login/index.vue"),
  },
  {
    path: "/auth/callback",
    component: () => import("@/pages/auth/callback.vue"),
  },
  // 内页统一套 AppLayout
  {
    path: "/",
    component: AppLayout,
    children: [
      {
        path: "",
        component: () => import("@/pages/index.vue"),
      },
      {
        path: "chat",
        component: () => import("@/pages/chat/index.vue"),
      },
      {
        path: "task/:task_id",
        component: () => import("@/pages/task/index.vue"),
        props: true,
      },
      {
        path: "example/:id",
        component: () => import("@/pages/example/[id].vue"),
        props: true,
      },
    ],
  },
  // 知识库独立路由 — 非贡献者显示全屏权限页
  {
    path: "/knowledge",
    component: () => import("@/pages/knowledge/index.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
