<template>
  <div id="app">
    <a-config-provider :locale="zhCN">
      <router-view />
    </a-config-provider>
  </div>
</template>

<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { useAuthStore } from './stores/auth'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    authStore.token = token
    try {
      await authStore.fetchUser()
    } catch {
      localStorage.removeItem('token')
      router.push('/login')
    }
  } else {
    router.push('/login')
  }
})
</script>

<style>
#app {
  min-height: 100vh;
  background: #141514;
  color: #e3e3e3;
}
</style>
