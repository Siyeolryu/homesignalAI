-- ============================================================================
-- HomeSignal AI - 대화형 챗봇을 위한 Conversation History 테이블
-- ============================================================================
-- 목적: 세션별 대화 히스토리 저장 및 관리, 진짜 대화형 RAG 챗봇 구현
-- 작성일: 2026-03-20
-- ============================================================================

-- ============================================================================
-- 1. conversation_sessions 테이블 (대화 세션 관리)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세션 식별 및 메타데이터
    session_id TEXT UNIQUE NOT NULL,  -- 클라이언트 생성 또는 서버 할당 세션 ID
    user_id TEXT,  -- 사용자 식별자 (익명 허용)

    -- 대화 컨텍스트
    region TEXT DEFAULT '동대문구',  -- 주요 관심 지역
    initial_query TEXT,  -- 대화 시작 질문

    -- 대화 상태
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired')),
    message_count INT DEFAULT 0,  -- 메시지 수 (성능 최적화용)

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'  -- 세션 만료 (24시간)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS conversation_sessions_session_id_idx
ON conversation_sessions (session_id);

CREATE INDEX IF NOT EXISTS conversation_sessions_status_idx
ON conversation_sessions (status);

CREATE INDEX IF NOT EXISTS conversation_sessions_expires_at_idx
ON conversation_sessions (expires_at);


-- ============================================================================
-- 2. conversation_messages 테이블 (메시지 히스토리)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세션 연결
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,

    -- 메시지 내용
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- 메시지 메타데이터
    sequence_number INT NOT NULL,  -- 세션 내 메시지 순서 (0부터 시작)

    -- RAG 컨텍스트 (assistant 메시지만 해당)
    forecast_data JSONB,  -- 예측 데이터 스냅샷
    news_sources JSONB,  -- 참조한 뉴스 문서 목록
    election_signals JSONB,  -- MCP에서 가져온 선거 공약 데이터
    planner_metadata JSONB,  -- Query Planner 디버그 정보

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS conversation_messages_session_id_idx
ON conversation_messages (session_id);

CREATE INDEX IF NOT EXISTS conversation_messages_session_sequence_idx
ON conversation_messages (session_id, sequence_number);

CREATE INDEX IF NOT EXISTS conversation_messages_created_at_idx
ON conversation_messages (created_at DESC);


-- ============================================================================
-- 3. 자동 업데이트 트리거 (updated_at, last_message_at)
-- ============================================================================

-- 세션 updated_at 자동 갱신
CREATE OR REPLACE FUNCTION update_conversation_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversation_sessions_updated_at_trigger
BEFORE UPDATE ON conversation_sessions
FOR EACH ROW
EXECUTE FUNCTION update_conversation_session_timestamp();


-- 메시지 추가 시 세션 last_message_at 및 message_count 갱신
CREATE OR REPLACE FUNCTION update_session_on_message_insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation_sessions
    SET
        last_message_at = NEW.created_at,
        message_count = message_count + 1,
        updated_at = NEW.created_at
    WHERE id = NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversation_messages_insert_trigger
AFTER INSERT ON conversation_messages
FOR EACH ROW
EXECUTE FUNCTION update_session_on_message_insert();


-- ============================================================================
-- 4. RPC 함수: 대화 히스토리 조회
-- ============================================================================

-- 4.1 세션 생성 또는 조회
CREATE OR REPLACE FUNCTION get_or_create_conversation_session(
    p_session_id TEXT,
    p_user_id TEXT DEFAULT NULL,
    p_region TEXT DEFAULT '동대문구',
    p_initial_query TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    session_id TEXT,
    user_id TEXT,
    region TEXT,
    status TEXT,
    message_count INT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ
) AS $$
DECLARE
    v_session_id UUID;
BEGIN
    -- 기존 세션 조회
    SELECT cs.id INTO v_session_id
    FROM conversation_sessions cs
    WHERE cs.session_id = p_session_id
    AND cs.status = 'active'
    AND cs.expires_at > NOW();

    -- 세션이 없으면 생성
    IF v_session_id IS NULL THEN
        INSERT INTO conversation_sessions (session_id, user_id, region, initial_query)
        VALUES (p_session_id, p_user_id, p_region, p_initial_query)
        RETURNING conversation_sessions.id INTO v_session_id;
    END IF;

    -- 세션 정보 반환
    RETURN QUERY
    SELECT
        cs.id,
        cs.session_id,
        cs.user_id,
        cs.region,
        cs.status,
        cs.message_count,
        cs.created_at,
        cs.updated_at,
        cs.last_message_at
    FROM conversation_sessions cs
    WHERE cs.id = v_session_id;
END;
$$ LANGUAGE plpgsql;


-- 4.2 대화 히스토리 조회 (최근 N개 메시지)
CREATE OR REPLACE FUNCTION get_conversation_history(
    p_session_id TEXT,
    p_limit INT DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    role TEXT,
    content TEXT,
    sequence_number INT,
    forecast_data JSONB,
    news_sources JSONB,
    election_signals JSONB,
    planner_metadata JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.id,
        cm.role,
        cm.content,
        cm.sequence_number,
        cm.forecast_data,
        cm.news_sources,
        cm.election_signals,
        cm.planner_metadata,
        cm.created_at
    FROM conversation_messages cm
    INNER JOIN conversation_sessions cs ON cm.session_id = cs.id
    WHERE cs.session_id = p_session_id
    ORDER BY cm.sequence_number ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- 4.3 메시지 저장
CREATE OR REPLACE FUNCTION save_conversation_message(
    p_session_id TEXT,
    p_role TEXT,
    p_content TEXT,
    p_forecast_data JSONB DEFAULT NULL,
    p_news_sources JSONB DEFAULT NULL,
    p_election_signals JSONB DEFAULT NULL,
    p_planner_metadata JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_session_uuid UUID;
    v_sequence_number INT;
    v_message_id UUID;
BEGIN
    -- 세션 UUID 조회
    SELECT id INTO v_session_uuid
    FROM conversation_sessions
    WHERE session_id = p_session_id;

    IF v_session_uuid IS NULL THEN
        RAISE EXCEPTION 'Session not found: %', p_session_id;
    END IF;

    -- 다음 sequence_number 계산
    SELECT COALESCE(MAX(sequence_number), -1) + 1 INTO v_sequence_number
    FROM conversation_messages
    WHERE session_id = v_session_uuid;

    -- 메시지 저장
    INSERT INTO conversation_messages (
        session_id,
        role,
        content,
        sequence_number,
        forecast_data,
        news_sources,
        election_signals,
        planner_metadata
    )
    VALUES (
        v_session_uuid,
        p_role,
        p_content,
        v_sequence_number,
        p_forecast_data,
        p_news_sources,
        p_election_signals,
        p_planner_metadata
    )
    RETURNING id INTO v_message_id;

    RETURN v_message_id;
END;
$$ LANGUAGE plpgsql;


-- 4.4 만료된 세션 정리
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INT AS $$
DECLARE
    v_deleted_count INT;
BEGIN
    WITH deleted AS (
        DELETE FROM conversation_sessions
        WHERE expires_at < NOW()
        AND status != 'completed'
        RETURNING id
    )
    SELECT COUNT(*) INTO v_deleted_count FROM deleted;

    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;


-- 4.5 세션 완료 처리
CREATE OR REPLACE FUNCTION complete_conversation_session(
    p_session_id TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_updated_count INT;
BEGIN
    UPDATE conversation_sessions
    SET status = 'completed', updated_at = NOW()
    WHERE session_id = p_session_id
    AND status = 'active';

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;

    RETURN v_updated_count > 0;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- 5. Row Level Security (RLS) 정책
-- ============================================================================
-- 주의: Supabase에서 RLS 활성화 시 service_role key 사용 필요

ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- service_role은 모든 접근 허용
CREATE POLICY "Service role has full access to conversation_sessions"
ON conversation_sessions
FOR ALL
TO service_role
USING (true);

CREATE POLICY "Service role has full access to conversation_messages"
ON conversation_messages
FOR ALL
TO service_role
USING (true);

-- authenticated 사용자는 자신의 세션만 조회 가능 (선택사항)
-- CREATE POLICY "Users can read own sessions"
-- ON conversation_sessions
-- FOR SELECT
-- TO authenticated
-- USING (user_id = auth.uid()::text);


-- ============================================================================
-- 완료 메시지
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 007: Conversation tables created successfully';
    RAISE NOTICE '   - conversation_sessions table with auto-expiry (24h)';
    RAISE NOTICE '   - conversation_messages table with CASCADE delete';
    RAISE NOTICE '   - Auto-update triggers for timestamps and message_count';
    RAISE NOTICE '   - RPC functions: get_or_create_session, get_history, save_message';
    RAISE NOTICE '   - RLS policies enabled (service_role access)';
END $$;
