<template>
  <div class="media-detail-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>媒体详情</h2>
          <a-button @click="$router.push('/home')">
            <LeftOutlined /> 返回
          </a-button>
        </div>
      </a-layout-header>

      <a-layout-content class="content" v-if="media">
        <a-row :gutter="24">
          <a-col :span="8">
            <img
              :src="media.poster_url || '/placeholder.png'"
              class="poster"
              :alt="media.title"
            />
          </a-col>
          <a-col :span="16">
            <div class="info">
              <h1>{{ media.title_cn || media.title }}</h1>
              <p class="year" v-if="media.year">{{ media.year }}</p>

              <a-tag :color="getStatusColor(media.status)">
                {{ getStatusText(media.status) }}
              </a-tag>

              <p class="overview" v-if="media.overview">{{ media.overview }}</p>

              <div class="actions">
                <a-button
                  type="primary"
                  size="large"
                  :loading="transferLoading"
                  :disabled="media.status === 'ready'"
                  @click="handleTransfer"
                >
                  <DownloadOutlined />
                  {{ getActionText(media.status) }}
                </a-button>

                <a-button
                  size="large"
                  :disabled="media.status !== 'ready'"
                  @click="$router.push(`/player/${media.id}`)"
                >
                  <PlayCircleOutlined />
                  播放
                </a-button>

                <a-button danger @click="handleDelete">
                  <DeleteOutlined />
                  删除
                </a-button>
              </div>

              <a-progress
                v-if="media.status === 'transferring'"
                :percent="transferProgress"
                status="active"
              />
            </div>
          </a-col>
        </a-row>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  LeftOutlined,
  DownloadOutlined,
  PlayCircleOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { api } from '../api/request'

const route = useRoute()
const router = useRouter()

const media = ref(null)
const loading = ref(false)
const transferLoading = ref(false)
const transferProgress = ref(0)

onMounted(async () => {
  await fetchMedia()
})

const fetchMedia = async () => {
  try {
    const response = await api.get(`/media/${route.params.id}`)
    media.value = response.data
  } catch (error) {
    message.error('获取媒体信息失败')
    router.push('/home')
  }
}

const handleTransfer = async () => {
  if (!media.value) return

  transferLoading.value = true
  media.value.status = 'transferring'

  try {
    await api.post(`/transfer/${media.value.id}`)
    media.value.status = 'ready'
    message.success('转存成功')
    await fetchMedia()
  } catch (error) {
    media.value.status = 'failed'
    message.error('转存失败')
    await fetchMedia()
  } finally {
    transferLoading.value = false
  }
}

const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个媒体吗？',
    onOk: async () => {
      try {
        await api.delete(`/media/${route.params.id}`)
        message.success('删除成功')
        router.push('/home')
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'default',
    scraped: 'blue',
    transferring: 'orange',
    ready: 'green',
    failed: 'red'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    scraped: '已削刮',
    transferring: '转存中',
    ready: '可播放',
    failed: '失败'
  }
  return texts[status] || status
}

const getActionText = (status) => {
  if (status === 'ready') return '已转存'
  if (status === 'transferring') return '转存中...'
  if (status === 'failed') return '重试转存'
  return '转存到网盘'
}
</script>

<style scoped>
.media-detail-container {
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
}

.poster {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.info h1 {
  margin-bottom: 8px;
}

.year {
  color: #888;
  margin-bottom: 16px;
}

.overview {
  margin: 16px 0;
  line-height: 1.6;
  color: #ccc;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
</style>
