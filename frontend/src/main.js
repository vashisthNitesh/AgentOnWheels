import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import { auth, loadMe } from './api'

const routes = [
  { path: '/login', component: () => import('./views/Login.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('./views/Dashboard.vue') },
  { path: '/control-tower', component: () => import('./views/ControlTower.vue') },
  { path: '/orders/:id(\\d+)', component: () => import('./views/OrderDetail.vue') },
  { path: '/r/:key', component: () => import('./views/ResourceList.vue') },
  { path: '/r/:key/new', component: () => import('./views/ResourceForm.vue') },
  { path: '/r/:key/:id(\\d+)', component: () => import('./views/ResourceDetail.vue') },
  { path: '/r/:key/:id(\\d+)/edit', component: () => import('./views/ResourceForm.vue') },
  { path: '/configuration', component: () => import('./views/ConfigHub.vue') },
  { path: '/:p(.*)*', component: () => import('./views/NotFound.vue') },
]
const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach(async to => {
  if (!auth.ready && localStorage.getItem('aow_access')) await loadMe()
  auth.ready = true
  if (!to.meta.public && !auth.user) return { path: '/login', query: { next: to.fullPath } }
  if (to.path === '/login' && auth.user) return '/dashboard'
})
createApp(App).use(router).mount('#app')
