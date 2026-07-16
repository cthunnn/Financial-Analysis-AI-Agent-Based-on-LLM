import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LLMOpsMetrics, DailyStats, RecentCall } from '@/api/llmops'

export const useLLMOpsStore = defineStore('llmops', () => {
  const metrics = ref<LLMOpsMetrics | null>(null)
  const dailyStats = ref<DailyStats[]>([])
  const recentCalls = ref<RecentCall[]>([])
  const isLoading = ref(false)

  function setMetrics(data: LLMOpsMetrics) {
    metrics.value = data
  }

  function setDailyStats(data: DailyStats[]) {
    dailyStats.value = data
  }

  function setRecentCalls(data: RecentCall[]) {
    recentCalls.value = data
  }

  return {
    metrics,
    dailyStats,
    recentCalls,
    isLoading,
    setMetrics,
    setDailyStats,
    setRecentCalls,
  }
})
