<template>
  <div class="dashboard">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>fnNAS媒体中心</h2>
          <div class="header-actions">
            <a-button @click="$router.push('/add-links')">
              <PlusOutlined /> 添加链接
            </a-button>
            <a-button @click="$router.push('/settings')">
              <SettingOutlined /> 设置
            </a-button>
          </div>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <a-row :gutter="24" class="stats-row">
          <a-col :span="6">
            <a-card class="stat-card" @click="$router.push('/home?category=movie')">
              <MovieIcon class="stat-icon" />
              <a-statistic title="电影" :value="stats.movie_count" />
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card class="stat-card" @click="$router.push('/home?category=tv')">
              <TvIcon class="stat-icon" />
              <a-statistic title="电视剧" :value="stats.tv_count" />
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card class="stat-card" @click="$router.push('/home?category=anime')">
              <AnimeIcon class="stat-icon" />
              <a-statistic title="动漫" :value="stats.anime_count" />
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card class="stat-card" @click="$router.push('/home?category=variety')">
              <VarietyIcon class="stat-icon" />
              <a-statistic title="综艺" :value="stats.variety_count" />
            </a-card>
          </a-col>
        </a-row>

        <a-row :gutter="24" class="mt-24">
          <a-col :span="12">
            <a-card title="存储状态">
              <a-progress
                :percent="storage.used_percent.toFixed(1)"
                :stroke-color="storage.used_percent > 80 ? '#ff4d4f' : '#1890ff'"
              />
              <p class="storage-info">
                已用: {{ formatSize(storage.used) }} / 总计: {{ formatSize(storage.total) }}
              </p>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="快捷操作">
              <a-space direction="vertical" style="width: 100%">
                <a-button block @click="$router.push('/add-links')">
                  <LinkOutlined /> 添加分享链接
                </a-button>
                <a-button block @click="handleScanSTRM">
                  <FolderScanOutlined /> 扫描本地STRM
                </a-button>
                <a-button block @click="handleCleanTask">
                  <DeleteOutlined /> 清理转存目录
                </a-button>
              </a-space>
            </a-card>
          </a-col>
        </a-row>

        <a-row :gutter="24" class="mt-24">
          <a-col :span="24">
            <a-card title="最近添加">
              <a-list :data-source="recentMedia" :loading="loading">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta
                      :title="item.title_cn || item.title"
                      :description="`${item.category} | ${formatDate(item.created_at)}`"
                    >
                      <template #avatar>
                        <a-avatar :src="item.poster_url" :size="48">
                          <template #icon><FileImageOutlined /></template>
                        </a-avatar>
                      </template>
                    </a-list-item-meta>
                    <template #actions>
                      <a-button type="link" size="small" @click="$router.push(`/media/${item.id}`)">
                        查看
                      </a-button>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </a-card>
          </a-col>
        </a-row>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  SettingOutlined,
  LinkOutlined,
  FolderScanOutlined,
  DeleteOutlined,
  FileImageOutlined
} from '@ant-design/icons-vue'
import { api } from '../api/request'

const router = useRouter()

const stats = ref({
  movie_count: 0,
  tv_count: 0,
  anime_count: 0,
  variety_count: 0,
  total: 0
})

const storage = ref({
  total: 0,
  used: 0,
  used_percent: 0
})

const recentMedia = ref([])
const loading = ref(false)

onMounted(async () => {
  await fetchStats()
  await fetchRecent()
  await fetchStorage()
})

const fetchStats = async () => {
  try {
    const response = await api.get('/dashboard/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchRecent = async () => {
  loading.value = true
  try {
    const response = await api.get('/dashboard/recent?limit=5')
    recentMedia.value = response.data
  } catch (error) {
    console.error('Failed to fetch recent:', error)
  } finally {
    loading.value = false
  }
}

const fetchStorage = async () => {
  try {
    const response = await api.get('/dashboard/storage')
    storage.value = response.data
  } catch (error) {
    console.error('Failed to fetch storage:', error)
  }
}

const handleScanSTRM = async () => {
  try {
    await api.post('/strm/scan', { directory: '/' })
    message.success('STRM扫描完成')
  } catch (error) {
    message.error('扫描失败')
  }
}

const handleCleanTask = async () => {
  try {
    const response = await api.post('/tasks/clean/0/run')
    if (response.data.success) {
      message.success('清理完成')
    }
  } catch (error) {
    message.error('清理失败')
  }
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.dashboard {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.content {
  padding: 24px;
}

.stats-row .stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stats-row .stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 8px;
  color: #1890ff;
}

.storage-info {
  margin-top: 8px;
  color: #888;
}

.mt-24 {
  margin-top: 24px;
}
</style>
