-- ============================================================
-- BizRithm Database Schema
-- PostgreSQL 16
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── Users ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'analyst',  -- admin, analyst, viewer
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(500),
    company_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- ── Datasets ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    file_type VARCHAR(20),  -- csv, xlsx, json
    file_size_bytes BIGINT,
    row_count INTEGER,
    column_count INTEGER,
    columns_meta JSONB,     -- {name, dtype, nulls, unique}
    table_name VARCHAR(100), -- Ingested postgres table name
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, ready, error
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── SQL Query History ────────────────────────────────────
CREATE TABLE IF NOT EXISTS sql_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    natural_language TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    execution_time_ms INTEGER,
    row_count INTEGER,
    status VARCHAR(50) DEFAULT 'success',  -- success, error, timeout
    error_message TEXT,
    result_preview JSONB,
    is_bookmarked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── Chat Messages ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    intent VARCHAR(100),        -- sql, forecast, insight, general
    metadata JSONB,             -- charts, sql, insight data
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── ML Predictions ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    feature_columns JSONB,
    forecast_periods INTEGER,
    metrics JSONB,    -- {mae, rmse, r2, mape}
    predictions JSONB,
    model_path VARCHAR(500),
    training_time_seconds FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── Reports ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(100),  -- executive, revenue, forecast, comprehensive
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    config JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── Business Insights ────────────────────────────────────
CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    insight_type VARCHAR(100),  -- anomaly, trend, recommendation, kpi
    title VARCHAR(255),
    content TEXT,
    severity VARCHAR(20) DEFAULT 'info',  -- info, warning, critical, opportunity
    metadata JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── Indexes ──────────────────────────────────────────────
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_sql_queries_user_id ON sql_queries(user_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX idx_ml_predictions_dataset ON ml_predictions(dataset_id);
CREATE INDEX idx_insights_user_dataset ON insights(user_id, dataset_id);

-- ── Updated_at trigger ───────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Default Admin User ───────────────────────────────────
-- Password: admin123 (bcrypt hashed)
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified, company_name)
VALUES (
    'admin@bizrithm.ai',
    'admin',
    'BizRithm Admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYxf.hC1zHXkfMi',
    'admin',
    TRUE,
    TRUE,
    'BizRithm Inc.'
) ON CONFLICT (email) DO NOTHING;
