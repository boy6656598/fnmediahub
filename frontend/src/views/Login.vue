<template>
  <div class="login-container">
    <div class="login-card">
      <h1>fnNAS媒体中心</h1>
      <p class="subtitle">登录您的网盘账号</p>

      <a-form :model="form" @finish="handleLogin">
        <a-form-item name="diskType" :rules="[{ required: true }]">
          <a-select v-model:value="form.diskType" placeholder="选择网盘类型">
            <a-select-option value="fnnas">飞牛OS云盘</a-select-option>
            <a-select-option value="webdav">WebDAV网盘</a-select-option>
          </a-select>
        </a-form-item>

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

        <template v-if="form.diskType === 'fnnas'">
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

        <template v-if="form.diskType === 'webdav'">
          <a-form-item name="host" :rules="[{ required: true, message: '请输入WebDAV地址' }]">
            <a-input v-model:value="form.host" placeholder="WebDAV地址" size="large">
              <template #prefix><GlobalOutlined /></template>
            </a-input>
          </a-form-item>
        </template>

        <a-form-item>
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
import { UserOutlined, LockOutlined, GlobalOutlined, KeyOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  diskType: 'fnnas',
  username: '',
  password: '',
  host: '',
  token: ''
})

const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const diskConfig = {}
    if (form.value.diskType === 'fnnas') {
      diskConfig.host = form.value.host
      diskConfig.token = form.value.token
    } else {
      diskConfig.host = form.value.host
      diskConfig.username = form.value.username
      diskConfig.password = form.value.password
    }

    const success = await authStore.login(
      form.value.username,
      form.value.password,
      form.value.diskType,
      diskConfig
    )

    if (success) {
      message.success('登录成功')
      router.push('/home')
    } else {
      message.error('登录失败')
    }
  } finally {
    loading.value = false
  }
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
  width: 400px;
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
