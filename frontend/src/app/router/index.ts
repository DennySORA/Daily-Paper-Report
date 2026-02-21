import { createRouter, createWebHistory } from 'vue-router'

// Import pages
import HomePage from '@/pages/HomePage.vue'
import ArchivePage from '@/pages/ArchivePage.vue'
import SourcesPage from '@/pages/SourcesPage.vue'
import StatusPage from '@/pages/StatusPage.vue'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      // Handle /index.html route (GitHub Pages default)
      path: '/index.html',
      redirect: '/',
    },
    {
      path: '/day/:date',
      name: 'day',
      component: HomePage,
    },
    {
      // Handle /day/:date.html routes (static file access)
      path: '/day/:date.html',
      redirect: (to) => ({ name: 'day', params: { date: to.params.date } }),
    },
    {
      path: '/archive',
      name: 'archive',
      component: ArchivePage,
    },
    {
      path: '/sources',
      name: 'sources',
      component: SourcesPage,
    },
    {
      path: '/status',
      name: 'status',
      component: StatusPage,
    },
  ],
})

export default router
