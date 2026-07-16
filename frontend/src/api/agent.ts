import apiClient from './index'

export interface AgentType {
  type: string
  name: string
  description: string
  capabilities: string[]
}

export const agentApi = {
  invoke: (data: {
    session_id: string
    query: string
    agent_types?: string[]
    parallel?: boolean
  }) => apiClient.post('/agent/invoke', data),

  getMemory: (sessionId: string) =>
    apiClient.get(`/agent/memory/${sessionId}`),

  clearMemory: (sessionId: string) =>
    apiClient.delete(`/agent/memory/${sessionId}`),

  listTypes: () =>
    apiClient.get<{ agents: AgentType[] }>('/agent/types'),
}
