<template>
  <div class="report-view">
    <header class="page-header">
      <h2>报告中心</h2>
      <button class="btn-primary" @click="generateReport">[+] 生成新报告</button>
    </header>

    <div v-if="reports.length === 0" class="empty-state">
      <p>暂无报告，点击上方按钮生成第一份投研报告。</p>
    </div>

    <div v-else class="report-list">
      <div v-for="report in reports" :key="report.id" class="report-card">
        <div class="report-header">
          <div class="report-title">{{ report.title }}</div>
          <span class="report-badge">{{ report.type }}</span>
        </div>
        <div class="report-meta">
          <span>日期: {{ report.date }}</span>
          <span>标的: {{ report.stock }}</span>
        </div>
        <p class="report-summary">{{ report.summary }}</p>
        <div class="report-actions">
          <button class="btn-text">查看详情</button>
          <button class="btn-text">下载报告</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const reports = ref([
  {
    id: 1,
    title: '贵州茅台(600519) 深度投研报告',
    type: '投研分析',
    date: '2024-01-15',
    stock: '600519',
    summary: '公司基本面稳健，高端白酒龙头地位稳固。当前估值处于历史中位偏上水平，建议关注旺季动销数据与渠道改革进展。',
  },
  {
    id: 2,
    title: '宁德时代(300750) 风险评估报告',
    type: '风险评估',
    date: '2024-01-14',
    stock: '300750',
    summary: '行业竞争格局加剧，二线电池厂商产能扩张带来价格压力。但公司技术壁垒与客户结构优势明显，整体风险可控。',
  },
  {
    id: 3,
    title: '科技板块 Q1 投资策略',
    type: '策略建议',
    date: '2024-01-13',
    stock: '板块分析',
    summary: 'AI算力需求持续增长，半导体周期复苏信号明确。建议超配AI芯片与光模块，标配消费电子，低配传统软件。',
  },
])

function generateReport() {
  alert('报告生成功能已触发，请在智能对话页面输入分析请求。')
  // TODO: 跳转到对话页面并预填分析请求
}
</script>

<style scoped>
.report-view { padding: 24px; height: 100%; overflow-y: auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h2 { font-size: 20px; color: #e0e6ed; margin: 0; font-weight: 600; }
.btn-primary { padding: 8px 20px; background: #3182ce; border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 14px; font-weight: 500; transition: background 0.2s; }
.btn-primary:hover { background: #2c5282; }

.empty-state { display: flex; align-items: center; justify-content: center; height: 200px; color: #718096; font-size: 14px; }

.report-list { display: flex; flex-direction: column; gap: 16px; }
.report-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; transition: border-color 0.2s; }
.report-card:hover { border-color: rgba(99,179,237,0.2); }
.report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.report-title { font-size: 15px; font-weight: 600; color: #e0e6ed; }
.report-badge { padding: 3px 10px; background: rgba(99,179,237,0.15); border-radius: 12px; font-size: 12px; color: #63b3ed; }
.report-meta { display: flex; gap: 16px; font-size: 12px; color: #718096; margin-bottom: 10px; }
.report-summary { font-size: 13px; color: #a0aec0; margin: 0 0 12px; line-height: 1.6; }
.report-actions { display: flex; gap: 12px; }
.btn-text { background: none; border: none; color: #63b3ed; cursor: pointer; font-size: 13px; padding: 0; }
.btn-text:hover { text-decoration: underline; }
</style>
