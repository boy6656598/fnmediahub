<template>
  <div class="home-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>fnNAS媒体中心</h2>
          <div class="header-actions">
            <a-button type="primary" @click="$router.push('/add-links')">
              <PlusOutlined /> 添加链接
            </a-button>
            <a-button @click="$router.push('/settings')">
              <SettingOutlined /> 设置
            </a-button>
            <a-dropdown>
              <a-avatar>{{ user?.username?.[0]?.toUpperCase() || 'U' }}</a-avatar>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="logout" @click="handleLogout">退出登录</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <div class="filter-bar">
          <a-input-search
            v-model:value="keyword"
            placeholder="搜索媒体..."
            style="width: 300px"
            @search="handleSearch"
          />
          <a-select v-model:value="mediaType" style="width: 120px" @change="handleSearch">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="movie">电影</a-select-option>
            <a-select-option value="tv">剧集</a-select-option>
          </a-select>
          <a-select v-model:value="status" style="width: 120px" @change="handleSearch">
            <a-select-option value="">全部状态</a-select-option>
            <a-select-option value="pending">待处理</a-select-option>
            <a-select-option value="scraped">已削刮</a-select-option>
            <a-select-option value="transferring">转存中</a-select-option>
            <a-select-option value="ready">可播放</a-select-option>
          </a-select>
        </div>

        <a-spin :spinning="loading">
          <div class="media-grid">
            <MediaCard
              v-for="item in mediaList"
              :key="item.id"
              :media="item"
              @click="$router.push(`/media/${item.id}`)"
            />
          </div>
        </a-spin>

        <div class="pagination" v-if="total > 0">
          <a-pagination
            v-model:current="page"
            :total="total"
            :pageSize="pageSize"
            @change="handlePageChange"
            show-quick-jumper
          />
        </div>

        <a-empty v-if="!loading && mediaList.length === 0" description="暂无媒体">
          <a-button type="primary" @click="$router.push('/add-links')">添加链接</a-button>
        </a-empty>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined, SettingOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useMediaStore } from '../stores/media'
import MediaCard from '../components/MediaCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const mediaStore = useMediaStore()

const keyword = ref('')
const mediaType = ref('')
const status = ref('')

const user = computed(() => authStore.user)
const mediaList = computed(() => mediaStore.mediaList)
const total = computed(() => mediaStore.total)
const page = computed({
  get: () => mediaStore.page,
  set: (val) => mediaStore.setPage(val)
})
const pageSize = computed(() => mediaStore.pageSize)
const loading = computed(() => mediaStore.loading)

onMounted(() => {
  mediaStore.fetchMediaList()
})

const handleSearch = () => {
  mediaStore.fetchMediaList({
    keyword: keyword.value,
    media_type: mediaType.value,
    status: status.value
  })
}

const handlePageChange = (newPage) => {
  mediaStore.fetchMediaList({
    keyword: keyword.value,
    media_type: mediaType.value,
    status: status.value
  })
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
  message.success('已退出登录')
}
</script>

<style scoped>
.home-container {
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
  align-items: center;
}

.content {
  padding: 24px;
  min-height: calc(100vh - 64px);
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.pagination {
  margin-top: 32px;
  text-align: center;
}
</style>
