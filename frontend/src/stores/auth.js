import { defineStore } from 'pinia'
import { api } from '../api/request'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
    diskStatus: null
  }),

  actions: {
    async login(username, password, diskType = 'fnnas', diskConfig = {}) {
      try {
        const response = await api.post('/auth/login', {
          username,
          password,
          disk_type: diskType,
          disk_config: diskConfig
        })
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        await this.fetchUser()
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },

    async fetchUser() {
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
        await this.fetchDiskStatus()
      } catch (error) {
        throw error
      }
    },

    async fetchDiskStatus() {
      try {
        const response = await api.get('/auth/disk-status')
        this.diskStatus = response.data
      } catch (error) {
        console.error('Failed to fetch disk status:', error)
      }
    },

    logout() {
      this.token = ''
      this.user = null
      this.diskStatus = null
      localStorage.removeItem('token')
    }
  }
})
