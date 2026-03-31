<template>
  <div class="settings-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>设置</h2>
          <a-button @click="$router.push('/')">
            <LeftOutlined /> 返回
          </a-button>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <a-card title="网盘配置" class="settings-card">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="网盘类型">
              {{ diskTypeText }}
            </a-descriptions-item>
            <a-descriptions-item label="连接状态">
              <a-badge :status="diskStatus?.connected ? 'success' : 'error'" />
              {{ diskStatus?.connected ? '已连接' : '未连接' }}
            </a-descriptions-item>
          </a-descriptions>

          <a-divider>配置信息</a-divider>

          <a-form layout="vertical" :model="diskConfig">
            <template v-if="diskType === 'fnnas'">
              <a-form-item label="飞牛OS地址">
                <a-input v-model:value="diskConfig.host" />
              </a-form-item>
              <a-form-item label="Token">
                <a-input-password v-model:value="diskConfig.token" />
              </a-form-item>
            </template>

            <template v-else-if="diskType === 'webdav'">
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

            <template v-else-if="diskType === '115'">
              <a-form-item label="115网盘">
                <a-tag color="green">已登录</a-tag>
                {{ diskConfig.user_name }}
              </a-form-item>
              <a-form-item>
                <a-space>
                  <a-button @click="handleClearSecurity">清理安全码</a-button>
                  <a-button @click="handleLogout115">退出登录</a-button>
                </a-space>
              </a-form-item>
            </template>

            <a-form-item>
              <a-button type="primary" @click="saveDiskConfig">
                保存配置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <a-card title="转存目录配置" class="settings-card">
          <a-form layout="vertical" :model="transferConfig">
            <a-form-item label="转存目录">
              <a-input v-model:value="transferConfig.transferDir" placeholder="/media/转存" />
            </a-form-item>
            <a-form-item label="电影目录">
              <a-input v-model:value="transferConfig.movieDir" placeholder="电影" />
            </a-form-item>
            <a-form-item label="剧集目录">
              <a-input v-model:value="transferConfig.tvDir" placeholder="剧集" />
            </a-form-item>
            <a-form-item label="动漫目录">
              <a-input v-model:value="transferConfig.animeDir" placeholder="动漫" />
            </a-form-item>
            <a-form-item label="综艺目录">
              <a-input v-model:value="transferConfig.varietyDir" placeholder="综艺" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" @click="saveTransferConfig">
                保存配置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <a-card title="定时清理任务" class="settings-card">
          <a-form layout="vertical" :model="cleanConfig">
            <a-form-item label="清理周期">
              <a-select v-model:value="cleanConfig.scheduleType">
                <a-select-option value="daily">每日</a-select-option>
                <a-select-option value="weekly">每周</a-select-option>
                <a-select-option value="monthly">每月</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="清理时间" v-if="cleanConfig.scheduleType === 'daily'">
              <a-select v-model:value="cleanConfig.hour">
                <a-select-option v-for="h in 24" :key="h-1" :value="h-1">
                  {{ h-1 }}:00
                </a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="清理时间" v-if="cleanConfig.scheduleType === 'weekly'">
              <a-select v-model:value="cleanConfig.dayOfWeek">
                <a-select-option value="mon">周一</a-select-option>
                <a-select-option value="tue">周二</a-select-option>
                <a-select-option value="wed">周三</a-select-option>
                <a-select-option value="thu">周四</a-select-option>
                <a-select-option value="fri">周五</a-select-option>
                <a-select-option value="sat">周六</a-select-option>
                <a-select-option value="sun">周日</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="清理时间" v-if="cleanConfig.scheduleType === 'monthly'">
              <a-select v-model:value="cleanConfig.dayOfMonth">
                <a-select-option v-for="d in 28" :key="d" :value="d">
                  每月{{ d }}日
                </a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="保留最近文件数">
              <a-input-number v-model:value="cleanConfig.keepCount" :min="1" :max="100" />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button type="primary" @click="saveCleanConfig">
                  保存设置
                </a-button>
                <a-button @click="runCleanNow">
                  立即执行清理
                </a-button>
              </a-space>
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
import { api } from '../api/request'

const router = useRouter()
const authStore = useAuthStore()

const diskType = computed(() => authStore.diskStatus?.disk_type || 'fnnas')
const diskStatus = computed(() => authStore.diskStatus)

const diskTypeText = computed(() => {
  const types = { fnnas: '飞牛OS云盘', webdav: 'WebDAV网盘', '115': '115网盘' }
  return types[diskType.value] || diskType.value
})

const diskConfig = ref({
  host: '',
  token: '',
  username: '',
  password: '',
  user_name: ''
})

const transferConfig = ref({
  transferDir: '/media/转存',
  movieDir: '电影',
  tvDir: '剧集',
  animeDir: '动漫',
  varietyDir: '综艺'
})

const cleanConfig = ref({
  scheduleType: 'daily',
  hour: 3,
  dayOfWeek: 'sun',
  dayOfMonth: 1,
  keepCount: 5
})

const tmdbKey = ref('')

onMounted(async () => {
  if (diskStatus.value) {
    diskConfig.value = { ...diskStatus.value.disk_config }
  }
  
  await fetchCleanConfig()
})

const fetchCleanConfig = async () => {
  try {
    const response = await api.get('/tasks/clean')
    if (response.data.config) {
      cleanConfig.value = { ...cleanConfig.value, ...response.data.config }
    }
  } catch (error) {
    console.error('Failed to fetch clean config:', error)
  }
}

const saveDiskConfig = async () => {
  try {
    await authStore.login(
      authStore.user?.username || 'admin',
      '',
      diskType.value,
      diskConfig.value
    )
    message.success('配置已保存')
  } catch (error) {
    message.error('保存失败')
  }
}

const saveTransferConfig = async () => {
  try {
    await api.post('/settings/transfer', transferConfig.value)
    message.success('转存配置已保存')
  } catch (error) {
    message.error('保存失败')
  }
}

const saveCleanConfig = async () => {
  try {
    await api.post('/tasks/clean', cleanConfig.value)
    message.success('清理任务已配置')
  } catch (error) {
    message.error('保存失败')
  }
}

const runCleanNow = async () => {
  try {
    const response = await api.post('/tasks/clean/0/run')
    if (response.data.success) {
      message.success('清理完成')
    }
  } catch (error) {
    message.error('清理失败')
  }
}

const handleClearSecurity = async () => {
  try {
    await api.post('/tasks/clear-security')
    message.success('安全码已清理')
  } catch (error) {
    message.error('清理失败')
  }
}

const handleLogout115 = async () => {
  try {
    await api.post('/auth/115/logout')
    message.success('已退出115登录')
  } catch (error) {
    message.error('退出失败')
  }
}

const saveScraperConfig = () => {
  localStorage.setItem('tmdb_key', tmdbKey.value)
  message.success('削刮配置已保存')
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
