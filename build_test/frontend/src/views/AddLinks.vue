<template>
  <div class="add-links-container">
    <a-layout>
      <a-layout-header class="header">
        <div class="header-content">
          <h2>添加分享链接</h2>
          <a-button @click="$router.push('/home')">
            <LeftOutlined /> 返回
          </a-button>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <a-card title="批量添加分享链接">
          <a-form @finish="handleSubmit">
            <a-form-item label="分享链接">
              <a-textarea
                v-model:value="links"
                placeholder="每行一个分享链接，支持：&#10;百度网盘 / 阿里云盘 / PikPak / 115 / 夸克网盘"
                :rows="10"
              />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button type="primary" html-type="submit" :loading="loading">
                  开始削刮
                </a-button>
                <a-button @click="links = ''">清空</a-button>
              </a-space>
            </a-form-item>
          </a-form>

          <a-divider>支持的平台</a-divider>

          <div class="platforms">
            <a-tag color="blue">百度网盘</a-tag>
            <a-tag color="green">阿里云盘</a-tag>
            <a-tag color="orange">PikPak</a-tag>
            <a-tag color="purple">115</a-tag>
            <a-tag color="cyan">夸克网盘</a-tag>
            <a-tag color="red">迅雷云盘</a-tag>
          </div>
        </a-card>

        <a-card title="削刮结果" v-if="results.length > 0" class="results-card">
          <a-list :data-source="results">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.title || item.url"
                  :description="item.status === 'success' ? '削刮成功' : item.error"
                >
                  <template #avatar>
                    <a-badge :status="item.status === 'success' ? 'success' : 'error'" />
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { LeftOutlined } from '@ant-design/icons-vue'
import { api } from '../api/request'

const router = useRouter()
const links = ref('')
const loading = ref(false)
const results = ref([])

const handleSubmit = async () => {
  if (!links.value.trim()) {
    message.warning('请输入分享链接')
    return
  }

  const urlList = links.value.split('\n').filter(url => url.trim())
  if (urlList.length === 0) {
    message.warning('没有有效的链接')
    return
  }

  loading.value = true
  results.value = []

  try {
    const response = await api.post('/scrape/batch', { urls: urlList })
    results.value = response.data.results
    message.success('削刮完成')
  } catch (error) {
    message.error('削刮失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.add-links-container {
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
  margin: 0 auto;
}

.platforms {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.results-card {
  margin-top: 24px;
}
</style>
