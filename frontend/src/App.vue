<template>
  <router-view v-slot="{ Component, route }">
    <Transition name="page-fade" mode="out-in">
      <component :is="Component" :key="route.path" />
    </Transition>
  </router-view>
</template>

<script setup lang="ts">
// Root component — delegates to router
</script>

<style>
/* 页面过渡：极轻微的向上推动，几乎不可察觉的位移 */
.page-fade-enter-active {
  transition: transform 0.18s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
.page-fade-leave-active {
  transition: none;
}

.page-fade-enter-from {
  transform: translateY(4px);
}
.page-fade-enter-to {
  transform: translateY(0);
}

/* 减少动效偏好 */
@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active {
    transition: none;
  }
  .page-fade-enter-from {
    transform: none;
  }
}
</style>
