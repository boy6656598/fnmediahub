<template>
  <div class="player-container">
    <div class="player-header">
      <a-button @click="$router.back()">
        <LeftOutlined /> 返回
      </a-button>
      <h3>{{ media?.title }}</h3>
    </div>

    <div class="player-wrapper">
      <video
        ref="videoRef"
        :src="streamUrl"
        controls
        autoplay
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
      ></video>
    </div>

    <div v-if="!streamUrl" class="loading">
      <a-spin size="large" />
      <p>正在加载视频...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { LeftOutlined } from '@ant-design/icons-vue'
import { api } from '../api/request'

const route = useRoute()
const router = useRouter()

const videoRef = ref(null)
const media = ref(null)
const streamUrl = ref('')
const loading = ref(true)

let savePositionTimer = null

onMounted(async () => {
  await fetchMedia()
  startPositionSave()
})

onUnmounted(() => {
  if (savePositionTimer) {
    clearInterval(savePositionTimer)
    savePosition()
  }
})

const fetchMedia = async () => {
  try {
    const response = await api.get(`/media/${route.params.id}`)
    media.value = response.data

    const streamResponse = await api.get(`/player/${route.params.id}/stream`)
    streamUrl.value = streamResponse.data.stream_url

    if (streamResponse.data.play_position && videoRef.value) {
      videoRef.value.currentTime = streamResponse.data.play_position
    }
  } catch (error) {
    message.error('获取播放信息失败')
    router.back()
  } finally {
    loading.value = false
  }
}

const handleTimeUpdate = () => {
}

const handleLoadedMetadata = () => {
  if (media.value?.play_position && videoRef.value) {
    videoRef.value.currentTime = media.value.play_position
  }
}

const startPositionSave = () => {
  savePositionTimer = setInterval(() => {
    savePosition()
  }, 30000)
}

const savePosition = async () => {
  if (videoRef.value && media.value) {
    const position = Math.floor(videoRef.value.currentTime)
    try {
      await api.put(`/player/${media.value.id}/position`, { position })
    } catch (error) {
      console.error('Failed to save position:', error)
    }
  }
}
</script>

<style scoped>
.player-container {
  min-height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
}

.player-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #1f1f1f;
}

.player-header h3 {
  color: #fff;
  margin: 0;
}

.player-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

video {
  max-width: 100%;
  max-height: calc(100vh - 100px);
  border-radius: 8px;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #fff;
}
</style>
