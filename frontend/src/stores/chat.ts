import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  agent_type?: string
  sources?: Array<{ content: string; score: number }>
  token_usage?: { total: number }
  latency_ms?: number
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const sessionId = ref(`session_${Date.now()}`)
  const isLoading = ref(false)
  const enableRAG = ref(true)
  const error = ref<string | null>(null)

  function addMessage(msg: ChatMessage) {
    messages.value.push(msg)
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = `session_${Date.now()}`
    error.value = null
  }

  function setError(msg: string) {
    error.value = msg
  }

  function clearError() {
    error.value = null
  }

  return {
    messages,
    sessionId,
    isLoading,
    enableRAG,
    error,
    addMessage,
    clearMessages,
    setError,
    clearError,
  }
})
