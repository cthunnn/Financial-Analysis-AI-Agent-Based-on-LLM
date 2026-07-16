<template>
  <div class="knowledge-view">
    <header class="page-header">
      <h2>知识库管理</h2>
      <button class="btn-primary" @click="showAddDialog = true">[+] 上传文档</button>
    </header>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value">{{ totalChunks.toLocaleString() }}</div>
        <div class="stat-label">知识片段数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">ChromaDB</div>
        <div class="stat-label">向量引擎</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">Cosine</div>
        <div class="stat-label">相似度算法</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ categories.length }}</div>
        <div class="stat-label">知识分类</div>
      </div>
    </div>

    <div class="section">
      <h3>知识分类</h3>
      <div class="category-grid">
        <div v-for="cat in categories" :key="cat.name" class="cat-chip">
          <span>{{ cat.name }}</span>
          <span class="cat-count">{{ cat.count.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <div v-if="showAddDialog" class="dialog-overlay" @click.self="showAddDialog = false">
      <div class="dialog-content">
        <h3>添加知识文档</h3>
        <input v-model="newTitle" placeholder="文档标题" class="dialog-input" />
        <select v-model="newCategory" class="dialog-input">
          <option value="">选择分类</option>
          <option value="news">财经新闻</option>
          <option value="report">年报/半年报</option>
          <option value="research">券商研报</option>
          <option value="regulation">金融法规</option>
          <option value="internal">内部知识</option>
        </select>
        <textarea v-model="newContent" placeholder="输入文档内容..." class="dialog-textarea" rows="6"></textarea>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showAddDialog = false">取消</button>
          <button class="btn-primary" @click="addKnowledge" :disabled="!newTitle || !newContent">确认添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const totalChunks = ref(2847)
const showAddDialog = ref(false)
const newTitle = ref('')
const newCategory = ref('')
const newContent = ref('')

const categories = ref([
  { name: '财经新闻', count: 856 },
  { name: '年报/半年报', count: 1203 },
  { name: '券商研报', count: 412 },
  { name: '金融法规', count: 156 },
  { name: '内部知识', count: 220 },
])

function addKnowledge() {
  if (!newTitle.value || !newContent.value) return
  showAddDialog.value = false
  newTitle.value = ''
  newContent.value = ''
  newCategory.value = ''
  totalChunks.value += 1
}
</script>

<style scoped>
.knowledge-view { padding: 24px; height: 100%; overflow-y: auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-header h2 { font-size: 20px; color: #e0e6ed; margin: 0; font-weight: 600; }
.btn-primary { padding: 8px 20px; background: #3182ce; border: none; border-radius: 8px; color: white; cursor: pointer; font-size: 14px; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; text-align: center; }
.stat-value { font-size: 24px; font-weight: 700; color: #63b3ed; }
.stat-label { font-size: 12px; color: #718096; margin-top: 4px; }

.section { margin-bottom: 24px; }
.section h3 { font-size: 15px; color: #e0e6ed; margin: 0 0 16px; font-weight: 600; }
.category-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.cat-chip { display: flex; align-items: center; gap: 8px; padding: 10px 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; font-size: 13px; color: #a0aec0; }
.cat-count { background: rgba(99,179,237,0.15); padding: 2px 10px; border-radius: 10px; font-size: 12px; color: #63b3ed; }

.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.dialog-content { background: #1a1f35; border: 1px solid rgba(99,179,237,0.25); border-radius: 16px; padding: 24px; width: 500px; }
.dialog-content h3 { font-size: 18px; color: #e0e6ed; margin: 0 0 16px; }
.dialog-input, .dialog-textarea { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(99,179,237,0.15); border-radius: 8px; padding: 10px 14px; color: #e0e6ed; font-size: 14px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; }
.dialog-textarea { resize: vertical; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 12px; }
.btn-cancel { padding: 8px 20px; background: none; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; color: #a0aec0; cursor: pointer; font-size: 14px; }
</style>
