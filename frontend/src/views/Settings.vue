<template>
  <div class="settings-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>设置</h2>
          <a-button @click="$router.push('/home')">
            <LeftOutlined /> 返回
          </a-button>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <a-card title="网盘配置" class="settings-card">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="网盘类型">
              {{ diskStatus?.disk_type === 'fnnas' ? '飞牛OS云盘' : 'WebDAV网盘' }}
            </a-descriptions-item>
            <a-descriptions-item label="连接状态">
              <a-badge :status="diskStatus?.connected ? 'success' : 'error'" />
              {{ diskStatus?.connected ? '已连接' : '未连接' }}
            </a-descriptions-item>
          </a-descriptions>

          <a-divider>配置信息</a-divider>

          <a-form
            v-if="diskStatus"
            layout="vertical"
            :model="diskConfig"
          >
            <template v-if="diskStatus.disk_type === 'fnnas'">
              <a-form-item label="飞牛OS地址">
                <a-input v-model:value="diskConfig.host" />
              </a-form-item>
              <a-form-item label="Token">
                <a-input-password v-model:value="diskConfig.token" />
              </a-form-item>
            </template>

            <template v-else>
              <a-form-item label="WebDAV地址">
                <a-input v-model:value="diskConfig.host" />
              </a-form-item>
              <a-form-item label="用户名">
                <a-input v-model:value="diskConfig.username" />
              </a-form-item>
              <a-form-item label="密码">
                <a-input-password v-model:value="diskConfig.password" />
              </a-form-item>
            </template>

            <a-form-item>
              <a-button type="primary" @click="saveDiskConfig">
                保存配置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <a-card title="削刮配置" class="settings-card">
          <a-form layout="vertical">
            <a-form-item label="TMDB API Key">
              <a-input v-model:value="tmdbKey" placeholder="用于获取电影/剧集元数据" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="saveScraperConfig">
                保存配置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <a-card title="账号" class="settings-card">
          <p>用户名：{{ user?.username }}</p>
          <a-button danger @click="handleLogout">退出登录</a-button>
        </a-card>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { LeftOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const diskStatus = computed(() => authStore.diskStatus)

const diskConfig = ref({
  host: '',
  token: '',
  username: '',
  password: ''
})

const tmdbKey = ref('')

onMounted(async () => {
  if (diskStatus.value) {
    diskConfig.value = { ...diskStatus.value.disk_config }
  }
})

const saveDiskConfig = async () => {
  try {
    await authStore.login(
      user.value.username,
      '',
      diskStatus.value.disk_type,
      diskConfig.value
    )
    message.success('配置已保存')
  } catch (error) {
    message.error('保存失败')
  }
}

const saveScraperConfig = () => {
  localStorage.setItem('tmdb_key', tmdbKey.value)
  message.success('削刮配置已保存')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
}

.header {
  background: #1f1f1f;
  padding: 0 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header h2 {
  color: #fff;
  margin: 0;
}

.content {
  padding: 24px;
  max-width: 800px;
}

.settings-card {
  margin-bottom: 24px;
}
</style>
