import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const Dashboard = () => import('@/views/Dashboard.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard - Krevera Analytics'
    }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = (to.meta.title as string) || 'Krevera Analytics'
  next()
})

export default router
