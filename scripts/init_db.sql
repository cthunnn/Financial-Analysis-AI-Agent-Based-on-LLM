-- =====================================================
-- Financial AI Agent - 数据库初始化脚本
-- 适用于 PostgreSQL 15+ (TimescaleDB)
-- =====================================================

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建对话会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) DEFAULT '新对话',
    agent_types JSONB DEFAULT '[]',
    message_count INTEGER DEFAULT 0,
    last_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_session_created ON chat_sessions(session_id, created_at);

-- 创建消息记录表
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_type VARCHAR(50),
    token_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建 LLM 调用日志表
CREATE TABLE IF NOT EXISTS llm_call_logs (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(100),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    model VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    latency_ms FLOAT DEFAULT 0,
    cost_usd FLOAT DEFAULT 0,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    prompt_preview TEXT,
    response_preview TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_llm_daily ON llm_call_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_model_created ON llm_call_logs(model, created_at);
CREATE INDEX IF NOT EXISTS idx_llm_session ON llm_call_logs(session_id);

-- 创建知识文档表
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(50) NOT NULL,
    source VARCHAR(200),
    content_hash VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    chunk_count INTEGER DEFAULT 0,
    indexed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建文档分块表
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    document_id INTEGER REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    embedding_id VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chunk_doc ON document_chunks(document_id, chunk_index);

-- 创建数据管道表
CREATE TABLE IF NOT EXISTS data_pipelines (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    source_type VARCHAR(50),
    schedule_cron VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    last_run_at TIMESTAMPTZ
);

-- 创建管道运行日志表
CREATE TABLE IF NOT EXISTS data_pipeline_run_logs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    pipeline_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT
);

-- 创建 Prompt 版本表
CREATE TABLE IF NOT EXISTS prompt_versions (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50),
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT false,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建股票数据缓存表
CREATE TABLE IF NOT EXISTS stock_cache (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_date VARCHAR(20),
    data_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_code, data_type, data_date)
);
CREATE INDEX IF NOT EXISTS idx_stock_cache_ttl ON stock_cache(stock_code, data_type, updated_at);

-- ===== TimescaleDB 时序优化（如果可用） =====
-- 将 llm_call_logs 转换为超表以利用 TimescaleDB 的自动分区
-- SELECT create_hypertable('llm_call_logs', 'created_at', if_not_exists => TRUE);
