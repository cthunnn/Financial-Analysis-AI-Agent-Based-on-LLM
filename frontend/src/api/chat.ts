import apiClient from './index'

export interface ChatRequest {
  session_id: string
  message: string
  agent_type?: string
  stream: boolean
  enable_rag: boolean
}

export interface ChatResponse {
  session_id: string
  message: string
  agent_type: string
  sources?: Array<{ content: string; score: number; metadata?: Record<string, any> }>
  token_usage?: { total: number }
  latency_ms?: number
  session_created?: boolean
}

export const chatApi = {
  send: (data: ChatRequest) =>
    apiClient.post<ChatResponse>('/chat', data),
}
