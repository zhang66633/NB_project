import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    component: () => import("@/pages/index.vue"),
  },
  {
    path: "/login",
    component: () => import("@/pages/login/index.vue"),
  },
  {
    path: "/chat",
    component: () => import("@/pages/chat/index.vue"),
  },
  {
    path: "/task/:task_id",
    component: () => import("@/pages/task/index.vue"),
    props: true,
  },
  {
    path: "/example/:id",
    component: () => import("@/pages/example/[id].vue"),
    props: true,
  },
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
