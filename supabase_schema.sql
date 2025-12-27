-- GetHiredAlly Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- 1. USER PROFILES & LIMITS (create first - other tables reference these)

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS profile_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES user_profiles(id),
    service_name TEXT NOT NULL,
    limit_count INTEGER NOT NULL,
    limit_period TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. USER MANAGEMENT

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    profile_id UUID REFERENCES user_profiles(id),
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    admin_role TEXT,
    smart_questions_free_used BOOLEAN DEFAULT FALSE,
    preferred_ai_provider VARCHAR(20) DEFAULT 'auto',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_verification_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. SERVICE REGISTRY

CREATE TABLE IF NOT EXISTS services (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    route TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    is_coming_soon BOOLEAN DEFAULT FALSE,
    requires_xray BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. USAGE TRACKING

CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    service_name TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, service_name, period_start)
);

-- 5. PROMPT TEMPLATES

CREATE TABLE IF NOT EXISTS prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    template_type TEXT NOT NULL,
    category_id INTEGER,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. ANALYSIS SESSIONS & RESULTS

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    service_name TEXT NOT NULL,
    job_description_text TEXT NOT NULL,
    job_title TEXT,
    company_name TEXT,
    mode TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES analysis_sessions(id),
    report_markdown TEXT,
    structured_data JSONB,
    validation_status TEXT,
    validation_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. STATIC QUESTIONS DATABASE

CREATE TABLE IF NOT EXISTS interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    subcategory TEXT,
    question_text TEXT NOT NULL,
    why_they_ask TEXT,
    framework TEXT,
    answer_structure TEXT,
    good_elements TEXT[],
    bad_elements TEXT[],
    variations TEXT[],
    depth_levels TEXT[] NOT NULL,
    order_priority INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS questions_to_ask (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purpose TEXT NOT NULL,
    category TEXT NOT NULL,
    question_text TEXT NOT NULL,
    why_to_ask TEXT,
    good_timing TEXT,
    order_priority INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. INSERT DEFAULT DATA

-- Default profiles
INSERT INTO user_profiles (profile_name, display_name, description, is_default) VALUES
('standard', 'Standard User', 'Default free user with basic limits', true),
('special', 'Special User', 'Promotional or survey participant', false),
('vip', 'VIP User', 'Unlimited access for promoters', false)
ON CONFLICT (profile_name) DO NOTHING;

-- Default services
INSERT INTO services (id, display_name, description, icon, route, is_active, display_order) VALUES
('xray', 'Understand This Job', 'Decode what employers really want from the job description', '🔍', '/xray', true, 1),
('questions', 'Prepare for Questions', 'Know what they will ask and how to answer', '❓', '/questions', true, 2),
('playbook', 'Craft Your Answers', 'Build your personal interview playbook', '📖', '/playbook', false, 3)
ON CONFLICT (id) DO NOTHING;

-- Profile limits for standard user
INSERT INTO profile_limits (profile_id, service_name, limit_count, limit_period)
SELECT id, 'xray', 1, 'week' FROM user_profiles WHERE profile_name = 'standard'
UNION ALL
SELECT id, 'questions_static', 5, 'total' FROM user_profiles WHERE profile_name = 'standard'
UNION ALL
SELECT id, 'questions_dynamic', 1, 'week' FROM user_profiles WHERE profile_name = 'standard';

-- Profile limits for special user
INSERT INTO profile_limits (profile_id, service_name, limit_count, limit_period)
SELECT id, 'xray', 3, 'week' FROM user_profiles WHERE profile_name = 'special'
UNION ALL
SELECT id, 'questions_static', 5, 'total' FROM user_profiles WHERE profile_name = 'special'
UNION ALL
SELECT id, 'questions_dynamic', 3, 'week' FROM user_profiles WHERE profile_name = 'special';

-- Profile limits for vip user (-1 means unlimited)
INSERT INTO profile_limits (profile_id, service_name, limit_count, limit_period)
SELECT id, 'xray', 20, 'week' FROM user_profiles WHERE profile_name = 'vip'
UNION ALL
SELECT id, 'questions_static', -1, 'unlimited' FROM user_profiles WHERE profile_name = 'vip'
UNION ALL
SELECT id, 'questions_dynamic', 20, 'week' FROM user_profiles WHERE profile_name = 'vip';

-- 9. X-RAY SPECIFIC TABLES (for enhanced storage)

CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    raw_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xray_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_description_id UUID REFERENCES job_descriptions(id),
    user_id UUID REFERENCES users(id),
    depth_level TEXT NOT NULL,
    interviewer_type TEXT,
    report_markdown TEXT NOT NULL,
    structured_output JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE xray_analyses ENABLE ROW LEVEL SECURITY;

-- Policies for job_descriptions
CREATE POLICY "Users can view own job descriptions" ON job_descriptions
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE id = user_id));
CREATE POLICY "Users can insert own job descriptions" ON job_descriptions
    FOR INSERT WITH CHECK (user_id IS NOT NULL);

-- Policies for xray_analyses
CREATE POLICY "Users can view own analyses" ON xray_analyses
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE id = user_id));
CREATE POLICY "Users can insert own analyses" ON xray_analyses
    FOR INSERT WITH CHECK (user_id IS NOT NULL);

-- 10. SMART QUESTIONS (AI-Generated Personalized Questions)

CREATE TABLE IF NOT EXISTS smart_question_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    xray_analysis_id UUID REFERENCES xray_analyses(id) ON DELETE SET NULL,
    job_title TEXT NOT NULL,
    company_name TEXT,
    cv_provided BOOLEAN DEFAULT FALSE,
    weak_areas JSONB,
    personalized_questions JSONB,
    generation_model TEXT DEFAULT 'gemini-2.5-pro',
    input_tokens INTEGER,
    output_tokens INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_smart_questions_user_id ON smart_question_results(user_id);
CREATE INDEX IF NOT EXISTS idx_smart_questions_created_at ON smart_question_results(created_at DESC);

-- Enable RLS
ALTER TABLE smart_question_results ENABLE ROW LEVEL SECURITY;

-- Policies for smart_question_results
CREATE POLICY "Users can view own smart questions" ON smart_question_results
    FOR SELECT USING (user_id = (SELECT id FROM users WHERE id = user_id));
CREATE POLICY "Users can insert own smart questions" ON smart_question_results
    FOR INSERT WITH CHECK (user_id IS NOT NULL);

-- JSONB Structure Documentation:
-- weak_areas stores: [{"area": "...", "risk_level": "high|medium|low", "detection_reason": "...", "preparation_tip": "..."}]
-- personalized_questions stores: [{"category": "...", "question_text": "...", "personalized_context": "...", "why_they_ask": "...", "good_answer_example": "...", "what_to_avoid": "...", "source": "cv_gap|job_specific|..."}]

-- 11. AI USAGE LOGGING & PREFERENCES

CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    service_name VARCHAR(50) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    request_type VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_user_id ON ai_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_created_at ON ai_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_usage_service_provider ON ai_usage_logs(service_name, provider);

CREATE TABLE IF NOT EXISTS user_ai_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_xray_provider VARCHAR(20) DEFAULT 'claude',
    preferred_questions_provider VARCHAR(20) DEFAULT 'gemini',
    auto_select_cheapest BOOLEAN DEFAULT FALSE,
    show_provider_choice BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_ai_prefs_user_id ON user_ai_preferences(user_id);

-- 12. AI USAGE DAILY SUMMARY (for fast reporting)

CREATE TABLE IF NOT EXISTS ai_usage_daily_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ai_provider TEXT NOT NULL,
    service_type TEXT NOT NULL,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10, 4) DEFAULT 0,
    avg_response_time_ms INTEGER,
    success_rate DECIMAL(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, user_id, ai_provider, service_type)
);

CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON ai_usage_daily_summary(date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_summary_user ON ai_usage_daily_summary(user_id);
