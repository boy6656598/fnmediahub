<template>
  <div class="media-card" @click="$emit('click')">
    <div class="poster-wrapper">
      <img
        :src="media.poster_url || '/placeholder.png'"
        :alt="media.title"
        class="poster"
        loading="lazy"
      />
      <div class="overlay">
        <PlayCircleOutlined class="play-icon" />
      </div>
      <a-badge
        :status="getStatusBadge(media.status)"
        :text="getStatusText(media.status)"
        class="status-badge"
      />
    </div>
    <div class="info">
      <h4 class="title">{{ media.title_cn || media.title }}</h4>
      <p class="year" v-if="media.year">{{ media.year }}</p>
    </div>
  </div>
</template>

<script setup>
import { PlayCircleOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  media: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const getStatusBadge = (status) => {
  const badges = {
    pending: 'default',
    scraped: 'blue',
    transferring: 'processing',
    ready: 'success',
    failed: 'error'
  }
  return badges[status] || 'default'
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
</script>

<style scoped>
.media-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.media-card:hover {
  transform: translateY(-4px);
}

.poster-wrapper {
  position: relative;
  aspect-ratio: 2/3;
  border-radius: 8px;
  overflow: hidden;
  background: #2a2a2a;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.poster-wrapper:hover .overlay {
  opacity: 1;
}

.play-icon {
  font-size: 48px;
  color: #fff;
}

.status-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
}

.info {
  padding: 8px 0;
}

.title {
  margin: 0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #e3e3e3;
}

.year {
  margin: 4px 0 0;
  font-size: 12px;
  color: #888;
}
</style>
