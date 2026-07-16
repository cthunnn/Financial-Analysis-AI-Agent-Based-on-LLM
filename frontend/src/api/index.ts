import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('[API Error]', message)
    return Promise.reject(new Error(message))
  }
)

export default apiClient
export { API_BASE }
