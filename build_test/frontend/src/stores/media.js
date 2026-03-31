import { defineStore } from 'pinia'
import { api } from '../api/request'

export const useMediaStore = defineStore('media', {
  state: () => ({
    mediaList: [],
    currentMedia: null,
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false
  }),

  actions: {
    async fetchMediaList(params = {}) {
      this.loading = true
      try {
        const response = await api.get('/media', {
          params: {
            page: this.page,
            page_size: this.pageSize,
            ...params
          }
        })
        this.mediaList = response.data.items
        this.total = response.data.total
      } catch (error) {
        console.error('Failed to fetch media list:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchMedia(id) {
      try {
        const response = await api.get(`/media/${id}`)
        this.currentMedia = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch media:', error)
        return null
      }
    },

    async deleteMedia(id) {
      try {
        await api.delete(`/media/${id}`)
        this.mediaList = this.mediaList.filter(m => m.id !== id)
        return true
      } catch (error) {
        console.error('Failed to delete media:', error)
        return false
      }
    },

    setPage(page) {
      this.page = page
    },

    setPageSize(pageSize) {
      this.pageSize = pageSize
    }
  }
})
