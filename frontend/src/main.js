import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'

import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Home from './views/Home.vue'
import AddLinks from './views/AddLinks.vue'
import MediaDetail from './views/MediaDetail.vue'
import Player from './views/Player.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/home', name: 'Home', component: Home },
  { path: '/add-links', name: 'AddLinks', component: AddLinks },
  { path: '/media/:id', name: 'MediaDetail', component: MediaDetail },
  { path: '/player/:id', name: 'Player', component: Player },
  { path: '/settings', name: 'Settings', component: Settings }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(Antd)

app.mount('#app')
