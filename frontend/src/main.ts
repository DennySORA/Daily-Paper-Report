import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/main.css'

// Import pages
import HomePage from './pages/HomePage.vue'
import ArchivePage from './pages/ArchivePage.vue'
import SourcesPage from './pages/SourcesPage.vue'
import StatusPage from './pages/StatusPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
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

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
