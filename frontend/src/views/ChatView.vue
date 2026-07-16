<template>
  <div class="chat-view">
    <header class="chat-header">
      <div class="header-left">
        <h2>智能投研对话</h2>
        <span class="model-tag">{{ modelLabel }}</span>
      </div>
      <div class="header-right">
        <button class="btn-icon" @click="clearChat" title="清空对话">
          [ 清空 ]
        </button>
      </div>
    </header>

    <div class="chat-body" ref="chatBodyRef">
      <div v-if="store.messages.length === 0" class="welcome-panel">
        <div class="welcome-logo">FinAgent</div>
        <h3>金融分析 AI Agent 平台</h3>
        <p>基于 LLM + Agent + RAG 的智能投研助手，支持多Agent协同分析与知识库增强问答。</p>
        <div class="quick-prompts">
          <div class="prompt-label">快速体验：</div>
          <button class="prompt-chip" @click="quickAsk('分析贵州茅台600519的基本面和估值水平')">
            [分析] 贵州茅台基本面与估值
          </button>
          <button class="prompt-chip" @click="quickAsk('对宁德时代300750进行风险评估')">
            [风控] 宁德时代风险评估
          </button>
          <button class="prompt-chip" @click="quickAsk('分析当前市场行情，给出科技板块投资建议')">
            [策略] 科技板块投资建议
          </button>
        </div>
      </div>

      <div v-else class="message-list">
        <div
          v-for="(msg, idx) in store.messages"
          :key="idx"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? 'U' : 'AI' }}
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="sender-name">
                {{ msg.role === 'user' ? '你' : 'FinAgent' }}
              </span>
              <span v-if="msg.agent_type" class="agent-badge">
                {{ msg.agent_type }}
              </span>
            </div>
            <div class="message-text" v-html="renderMarkdown(msg.content)"></div>

            <div v-if="msg.sources && msg.sources.length > 0" class="sources-panel">
              <div class="sources-title">[参考来源]</div>
              <div v-for="(src, sidx) in msg.sources.slice(0, 3)" :key="sidx" class="source-item">
                <span class="source-score">{{ (src.score * 100).toFixed(0) }}%</span>
                <span class="source-text">{{ src.content }}</span>
              </div>
            </div>

            <div v-if="msg.token_usage || msg.latency_ms" class="message-meta">
              <span v-if="msg.token_usage">Tokens: {{ msg.token_usage.total }}</span>
              <span v-if="msg.latency_ms">延迟: {{ msg.latency_ms }}ms</span>
            </div>
          </div>
        </div>

        <div v-if="store.isLoading" class="message-item assistant">
          <div class="message-avatar">AI</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-footer">
      <div class="input-toolbar">
        <label class="toolbar-item">
          <input type="checkbox" v-model="store.enableRAG" />
          <span>启用 RAG 知识增强</span>
        </label>
      </div>
      <div class="input-row">
        <textarea
          v-model="inputMessage"
          class="input-area"
          placeholder="输入金融分析问题，例如：分析贵州茅台的基本面..."
          rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          @input="autoResize"
          ref="inputRef"
        ></textarea>
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="!inputMessage.trim() || store.isLoading"
        >
          {{ store.isLoading ? '...' : '>' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import { chatApi } from '@/api/chat'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const inputMessage = ref('')
const chatBodyRef = ref<HTMLElement>()
const inputRef = ref<HTMLTextAreaElement>()

const modelLabel = 'Qwen-Plus + RAG'

function renderMarkdown(text: string): string {
  try {
    return marked.parse(text, { async: false }) as string
  } catch {
    return text
  }
}

function autoResize() {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || store.isLoading) return

  store.addMessage({ role: 'user', content: text })
  inputMessage.value = ''
  store.isLoading = true
  await nextTick()
  scrollToBottom()

  try {
    const res = await chatApi.send({
      session_id: store.sessionId,
      message: text,
      enable_rag: store.enableRAG,
      stream: false,
    })

    store.addMessage({
      role: 'assistant',
      content: res.message,
      agent_type: res.agent_type,
      sources: res.sources,
      token_usage: res.token_usage,
      latency_ms: res.latency_ms,
    })
  } catch (e: any) {
    store.addMessage({
      role: 'assistant',
      content: `[错误] 请求失败: ${e.message || '未知错误'}`,
    })
  } finally {
    store.isLoading = false
    await nextTick()
    scrollToBottom()
  }
}

function quickAsk(question: string) {
  inputMessage.value = question
  sendMessage()
}

function clearChat() {
  store.clearMessages()
}

function scrollToBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}
</script>

<style scoped>
/* ===== 布局 ===== */
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0a0e1a;
}

/* ===== 头部 ===== */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(99, 179, 237, 0.15);
  background: linear-gradient(90deg, rgba(99, 179, 237, 0.08) 0%, transparent 100%);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  font-size: 18px;
  font-weight: 600;
  color: #e0e6ed;
  margin: 0;
}

.model-tag {
  padding: 4px 10px;
  background: rgba(99, 179, 237, 0.2);
  border-radius: 20px;
  font-size: 12px;
  color: #63b3ed;
}

.btn-icon {
  background: none;
  border: 1px solid rgba(99, 179, 237, 0.2);
  border-radius: 6px;
  color: #718096;
  cursor: pointer;
  font-size: 13px;
  padding: 6px 12px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(99, 179, 237, 0.15);
  color: #63b3ed;
}

/* ===== 消息区域 ===== */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 欢迎面板 */
.welcome-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #a0aec0;
}

.welcome-logo {
  font-size: 48px;
  font-weight: 800;
  color: #63b3ed;
  margin-bottom: 24px;
  letter-spacing: 2px;
}

.welcome-panel h3 {
  font-size: 24px;
  color: #e0e6ed;
  margin: 0 0 8px;
}

.welcome-panel p {
  font-size: 14px;
  color: #718096;
  margin: 0 0 32px;
  max-width: 480px;
  line-height: 1.7;
}

.quick-prompts {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.prompt-label {
  font-size: 13px;
  color: #4a5568;
  margin-bottom: 4px;
}

.prompt-chip {
  padding: 10px 20px;
  background: rgba(99, 179, 237, 0.08);
  border: 1px solid rgba(99, 179, 237, 0.2);
  border-radius: 24px;
  color: #a0aec0;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.prompt-chip:hover {
  background: rgba(99, 179, 237, 0.18);
  border-color: rgba(99, 179, 237, 0.4);
  color: #63b3ed;
  transform: translateY(-1px);
}

/* 消息列表 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message-item.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-item.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  background: rgba(99, 179, 237, 0.15);
  color: #63b3ed;
}

.message-item.assistant .message-avatar {
  background: rgba(104, 211, 145, 0.15);
  color: #68d391;
}

.message-content {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 14px 18px;
  min-width: 0;
}

.message-item.user .message-content {
  background: rgba(99, 179, 237, 0.1);
  border-color: rgba(99, 179, 237, 0.2);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.sender-name {
  font-size: 13px;
  font-weight: 600;
  color: #a0aec0;
}

.agent-badge {
  padding: 2px 8px;
  background: rgba(104, 211, 145, 0.15);
  border-radius: 10px;
  font-size: 11px;
  color: #68d391;
}

.message-text {
  font-size: 14px;
  line-height: 1.75;
  color: #cbd5e0;
  word-break: break-word;
}

.message-text :deep(strong) {
  color: #63b3ed;
}

.message-text :deep(h2),
.message-text :deep(h3) {
  color: #e0e6ed;
  margin: 16px 0 8px;
}

.message-text :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  font-size: 13px;
}

.message-text :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
}

.message-text :deep(th),
.message-text :deep(td) {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
  text-align: left;
}

.message-text :deep(th) {
  background: rgba(99, 179, 237, 0.1);
  color: #63b3ed;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

/* 参考来源 */
.sources-panel {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(99, 179, 237, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(99, 179, 237, 0.12);
}

.sources-title {
  font-size: 12px;
  color: #63b3ed;
  margin-bottom: 8px;
  font-weight: 600;
}

.source-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;
  color: #718096;
}

.source-score {
  color: #68d391;
  font-weight: 600;
  flex-shrink: 0;
  min-width: 36px;
}

.source-text {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 消息元数据 */
.message-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 11px;
  color: #4a5568;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #63b3ed;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ===== 输入区域 ===== */
.chat-footer {
  border-top: 1px solid rgba(99, 179, 237, 0.15);
  padding: 16px 24px;
  background: rgba(15, 22, 41, 0.9);
}

.input-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
}

.toolbar-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #718096;
  cursor: pointer;
  user-select: none;
}

.toolbar-item input[type="checkbox"] {
  accent-color: #63b3ed;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-area {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 12px;
  padding: 12px 16px;
  color: #e0e6ed;
  font-size: 14px;
  resize: none;
  outline: none;
  font-family: inherit;
  line-height: 1.5;
  transition: border-color 0.2s, background 0.2s;
}

.input-area:focus {
  border-color: rgba(99, 179, 237, 0.4);
  background: rgba(99, 179, 237, 0.05);
}

.input-area::placeholder {
  color: #4a5568;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #3182ce, #63b3ed);
  color: white;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(99, 179, 237, 0.4);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
