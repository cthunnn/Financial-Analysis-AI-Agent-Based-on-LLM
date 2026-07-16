<template>
  <div class="dashboard-view">
    <header class="page-header">
      <h2>金融数据看板</h2>
      <span class="update-time">更新于 {{ updateTime }}</span>
    </header>

    <div class="stock-cards">
      <div v-for="stock in stocks" :key="stock.code" class="stock-card">
        <div class="stock-top">
          <div class="stock-name">{{ stock.name }}</div>
          <div class="stock-code">{{ stock.code }}</div>
        </div>
        <div class="stock-price">&yen;{{ stock.price.toFixed(2) }}</div>
        <div class="stock-change" :class="stock.changePct >= 0 ? 'up' : 'down'">
          {{ stock.changePct >= 0 ? '+' : '' }}{{ stock.changePct.toFixed(2) }}%
        </div>
        <div class="stock-vol">成交量: {{ (stock.volume / 100000000).toFixed(2) }}亿</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="panel panel-arch">
        <h3>系统架构概览</h3>
        <div class="arch-list">
          <div class="arch-item">
            <span class="arch-tag tag-blue">Agent 编排层</span>
            <span>多 Agent 协同分析，意图分类，任务调度</span>
          </div>
          <div class="arch-item">
            <span class="arch-tag tag-green">RAG 知识增强</span>
            <span>混合检索 + Cross-Encoder 重排序 + GRAG 生成</span>
          </div>
          <div class="arch-item">
            <span class="arch-tag tag-purple">LLM 大模型层</span>
            <span>Qwen / DeepSeek / GPT，Function Calling 工具调用</span>
          </div>
          <div class="arch-item">
            <span class="arch-tag tag-orange">LLMOps 监控</span>
            <span>Token 计量，成本追踪，延迟监控，告警通知</span>
          </div>
          <div class="arch-item">
            <span class="arch-tag tag-red">DataOps 数据层</span>
            <span>Prefect 管道编排，ETL 调度，数据质量校验</span>
          </div>
        </div>
      </div>

      <div class="panel panel-features">
        <h3>核心能力</h3>
        <div class="feature-grid">
          <div class="feature-item">
            <div class="feature-name">智能投研对话</div>
            <div class="feature-desc">自然语言查询基本面、财务指标与估值</div>
          </div>
          <div class="feature-item">
            <div class="feature-name">多Agent协同</div>
            <div class="feature-desc">投研 + 风控 + 策略 Agent 并行协作</div>
          </div>
          <div class="feature-item">
            <div class="feature-name">RAG知识问答</div>
            <div class="feature-desc">基于金融知识库的精准检索与生成</div>
          </div>
          <div class="feature-item">
            <div class="feature-name">实时市场监控</div>
            <div class="feature-desc">行情异动预警与舆情实时追踪</div>
          </div>
          <div class="feature-item">
            <div class="feature-name">LLMOps运维</div>
            <div class="feature-desc">全量调用日志、成本分析与指标监控</div>
          </div>
          <div class="feature-item">
            <div class="feature-name">DataOps管道</div>
            <div class="feature-desc">可配置的金融数据 ETL 编排调度</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const updateTime = ref(new Date().toLocaleString('zh-CN'))

const stocks = ref([
  { code: '600519', name: '贵州茅台', price: 1688.00, changePct: 1.25, volume: 2800000000 },
  { code: '000858', name: '五粮液',   price: 142.50, changePct: -0.83, volume: 1200000000 },
  { code: '300750', name: '宁德时代', price: 198.30, changePct: 2.15, volume: 3500000000 },
  { code: '601318', name: '中国平安', price: 45.80,  changePct: 0.55, volume: 2200000000 },
])
</script>

<style scoped>
.dashboard-view { padding: 24px; height: 100%; overflow-y: auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 600; color: #e0e6ed; margin: 0; }
.update-time { font-size: 13px; color: #4a5568; }

.stock-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stock-card { background: linear-gradient(135deg, rgba(99,179,237,0.08), rgba(99,179,237,0.02)); border: 1px solid rgba(99,179,237,0.15); border-radius: 12px; padding: 20px; }
.stock-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.stock-name { font-size: 15px; font-weight: 600; color: #e0e6ed; }
.stock-code { font-size: 12px; color: #718096; }
.stock-price { font-size: 24px; font-weight: 700; color: #e0e6ed; margin-bottom: 6px; }
.stock-change { font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.stock-change.up { color: #fc8181; }
.stock-change.down { color: #68d391; }
.stock-vol { font-size: 12px; color: #4a5568; }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; }
.panel h3 { font-size: 15px; color: #e0e6ed; margin: 0 0 16px; font-weight: 600; }

.arch-list { display: flex; flex-direction: column; gap: 10px; }
.arch-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #a0aec0; }
.arch-tag { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.tag-blue { background: rgba(99,179,237,0.2); color: #63b3ed; }
.tag-green { background: rgba(104,211,145,0.2); color: #68d391; }
.tag-purple { background: rgba(183,148,244,0.2); color: #b794f4; }
.tag-orange { background: rgba(246,173,85,0.2); color: #f6ad55; }
.tag-red { background: rgba(252,129,129,0.2); color: #fc8181; }

.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.feature-item { padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
.feature-name { font-size: 13px; font-weight: 600; color: #e0e6ed; margin-bottom: 4px; }
.feature-desc { font-size: 12px; color: #718096; line-height: 1.5; }
</style>
