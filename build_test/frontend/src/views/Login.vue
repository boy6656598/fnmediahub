<template>
  <div class="login-container">
    <div class="login-card">
      <h1>fnNAS媒体中心</h1>
      <p class="subtitle">登录您的网盘账号</p>

      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="fnnas" tab="飞牛OS" />
        <a-tab-pane key="webdav" tab="WebDAV" />
        <a-tab-pane key="115" tab="115网盘" />
      </a-tabs>

      <a-form :model="form" @finish="handleLogin">
        <template v-if="activeTab === 'fnnas'">
          <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
            <a-input v-model:value="form.username" placeholder="用户名" size="large">
              <template #prefix><UserOutlined /></template>
            </a-input>
          </a-form-item>

          <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="form.password" placeholder="密码" size="large">
              <template #prefix><LockOutlined /></template>
            </a-input-password>
          </a-form-item>

          <a-form-item name="host" :rules="[{ required: true, message: '请输入飞牛OS地址' }]">
            <a-input v-model:value="form.host" placeholder="飞牛OS地址 (如 http://192.168.1.100:3000)" size="large">
              <template #prefix><GlobalOutlined /></template>
            </a-input>
          </a-form-item>

          <a-form-item name="token" :rules="[{ required: true, message: '请输入Token' }]">
            <a-input v-model:value="form.token" placeholder="Token" size="large">
              <template #prefix><KeyOutlined /></template>
            </a-input>
          </a-form-item>
        </template>

        <template v-if="activeTab === 'webdav'">
          <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
            <a-input v-model:value="form.username" placeholder="用户名" size="large">
              <template #prefix><UserOutlined /></template>
            </a-input>
          </a-form-item>

          <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="form.password" placeholder="密码" size="large">
              <template #prefix><LockOutlined /></template>
            </a-input-password>
          </a-form-item>

          <a-form-item name="host" :rules="[{ required: true, message: '请输入WebDAV地址' }]">
            <a-input v-model:value="form.host" placeholder="WebDAV地址" size="large">
              <template #prefix><GlobalOutlined /></template>
            </a-input>
          </a-form-item>
        </template>

        <template v-if="activeTab === '115'">
          <div v-if="!qrcodeVisible" class="qrcode-section">
            <a-button type="primary" size="large" block @click="showQRCode">
              <ScanOutlined /> 微信/支付宝扫码登录
            </a-button>
          </div>

          <div v-else class="qrcode-section">
            <div v-if="qrcodeLoading" class="qrcode-loading">
              <a-spin size="large" />
              <p>正在获取二维码...</p>
            </div>
            <div v-else-if="qrcodeData" class="qrcode-container">
              <img :src="qrcodeData.qrcode_url" alt="扫码登录" class="qrcode-image" />
              <p class="qrcode-hint">请使用微信或支付宝扫码登录</p>
              <a-button type="link" @click="qrcodeVisible = false">取消</a-button>
            </div>
          </div>
        </template>

        <a-form-item v-if="activeTab !== '115' || qrcodeVisible">
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <div class="platforms">
        <span>支持的平台：</span>
        <a-tag color="blue">百度网盘</a-tag>
        <a-tag color="green">阿里云盘</a-tag>
        <a-tag color="orange">PikPak</a-tag>
        <a-tag color="purple">115</a-tag>
        <a-tag color="cyan">夸克网盘</a-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, GlobalOutlined, KeyOutlined, ScanOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../api/request'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('fnnas')
const form = ref({
  diskType: 'fnnas',
  username: '',
  password: '',
  host: '',
  token: ''
})

const loading = ref(false)
const qrcodeVisible = ref(false)
const qrcodeLoading = ref(false)
const qrcodeData = ref(null)
const qrcodeUuid = ref('')
let qrcodePollTimer = null

const handleLogin = async () => {
  loading.value = true
  try {
    const diskConfig = {}

    if (activeTab.value === 'fnnas') {
      diskConfig.host = form.value.host
      diskConfig.token = form.value.token
    } else if (activeTab.value === 'webdav') {
      diskConfig.host = form.value.host
      diskConfig.username = form.value.username
      diskConfig.password = form.value.password
    }

    const success = await authStore.login(
      form.value.username,
      form.value.password,
      activeTab.value,
      diskConfig
    )

    if (success) {
      message.success('登录成功')
      router.push('/')
    } else {
      message.error('登录失败')
    }
  } finally {
    loading.value = false
  }
}

const showQRCode = async () => {
  qrcodeLoading.value = true
  qrcodeVisible.value = true

  try {
    const response = await api.post('/auth/115/qrcode')
    qrcodeData.value = response.data
    qrcodeUuid.value = response.data.uuid
    startQRCodePolling()
  } catch (error) {
    message.error('获取二维码失败')
    qrcodeVisible.value = false
  } finally {
    qrcodeLoading.value = false
  }
}

const startQRCodePolling = () => {
  qrcodePollTimer = setInterval(async () => {
    try {
      const response = await api.get(`/auth/115/qrcode/${qrcodeUuid.value}`)
      const status = response.data.status

      if (status === 'confirmed') {
        clearInterval(qrcodePollTimer)
        message.success('登录成功')
        router.push('/')
      } else if (status === 'expired') {
        clearInterval(qrcodePollTimer)
        message.warning('二维码已过期，请重新扫码')
        qrcodeVisible.value = false
      }
    } catch (error) {
      console.error('Check QRCode failed:', error)
    }
  }, 2000)
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-card h1 {
  text-align: center;
  color: #fff;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #888;
  margin-bottom: 30px;
}

.qrcode-section {
  text-align: center;
  padding: 20px 0;
}

.qrcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qrcode-image {
  width: 200px;
  height: 200px;
  border-radius: 8px;
}

.qrcode-hint {
  margin-top: 12px;
  color: #888;
}

.qrcode-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.platforms {
  margin-top: 20px;
  text-align: center;
  color: #666;
}

.platforms span {
  display: block;
  margin-bottom: 8px;
}
</style>
