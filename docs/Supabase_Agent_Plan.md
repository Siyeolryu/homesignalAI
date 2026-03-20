# Supabase 전문가 Agent 설계 문서

## 1. 개요

### 목적
- Supabase 데이터베이스 관리 작업을 자동화하는 전문 agent
- Migration 실행, 테이블 관리, RPC 함수 작성, 데이터 검증 등을 수행
- 대화형 인터페이스로 자연어 명령 처리

### 주요 기능
1. **Migration 관리**: SQL 파일 실행, 롤백, 검증
2. **스키마 관리**: 테이블/컬럼 생성/수정/삭제
3. **RPC 함수 관리**: 함수 작성, 테스트, 디버깅
4. **데이터 작업**: 조회, 분석, 백업
5. **성능 최적화**: 인덱스 분석, 쿼리 최적화
6. **RLS 정책**: Row Level Security 설정 및 검증

---

## 2. 아키텍처

### 2.1 컴포넌트 구조

```
src/shared/supabase_agent/
├── __init__.py
├── agent.py              # 메인 agent 클래스
├── tools/
│   ├── __init__.py
│   ├── migration.py      # Migration 실행 도구
│   ├── schema.py         # 스키마 관리 도구
│   ├── rpc.py            # RPC 함수 관리
│   ├── query.py          # 데이터 조회/분석
│   └── validation.py     # 검증 도구
├── prompts.py            # Agent 프롬프트
└── schemas.py            # Pydantic 스키마

scripts/
└── supabase_agent_cli.py # CLI 인터페이스
```

### 2.2 Agent 클래스 설계

```python
class SupabaseAgent:
    """Supabase 전문가 agent"""

    def __init__(self, ai_client: AIClient, supabase_client):
        self.ai_client = ai_client
        self.supabase = supabase_client
        self.tools = self._init_tools()

    async def execute(self, command: str) -> AgentResponse:
        """자연어 명령 실행"""
        # 1. 명령 분석 (AI)
        # 2. 도구 선택
        # 3. 실행
        # 4. 결과 반환

    def _init_tools(self):
        """사용 가능한 도구 초기화"""
        return {
            "run_migration": MigrationTool(self.supabase),
            "create_table": SchemaTool(self.supabase),
            "create_rpc": RPCTool(self.supabase),
            "query_data": QueryTool(self.supabase),
            "validate": ValidationTool(self.supabase),
        }
```

---

## 3. 도구 (Tools) 상세

### 3.1 Migration Tool

**기능**:
- Migration 파일 실행
- 검증 (테이블/함수 존재 확인)
- 롤백 (가능한 경우)

**API**:
```python
class MigrationTool:
    async def run_migration(self, file_path: str) -> MigrationResult
    async def verify_migration(self, migration_id: str) -> bool
    async def list_migrations(self) -> list[Migration]
```

**사용 예**:
```
Agent: "Migration 007을 실행해줘"
→ MigrationTool.run_migration("migrations/007_add_conversation_tables.sql")
```

### 3.2 Schema Tool

**기능**:
- 테이블 생성/수정/삭제
- 컬럼 추가/수정/삭제
- 인덱스 생성/삭제
- 외래키 설정

**API**:
```python
class SchemaTool:
    async def create_table(self, table_name: str, columns: list[Column]) -> bool
    async def add_column(self, table: str, column: Column) -> bool
    async def create_index(self, table: str, columns: list[str]) -> bool
    async def get_schema(self, table: str) -> TableSchema
```

**사용 예**:
```
Agent: "user_preferences 테이블에 theme 컬럼을 추가해줘"
→ SchemaTool.add_column("user_preferences", Column(name="theme", type="TEXT"))
```

### 3.3 RPC Tool

**기능**:
- PostgreSQL 함수 생성
- 함수 테스트
- 함수 목록 조회

**API**:
```python
class RPCTool:
    async def create_function(self, sql: str) -> bool
    async def test_function(self, name: str, params: dict) -> Any
    async def list_functions(self, pattern: str = None) -> list[Function]
```

**사용 예**:
```
Agent: "get_conversation_history 함수를 테스트해줘"
→ RPCTool.test_function("get_conversation_history", {"p_session_id": "test"})
```

### 3.4 Query Tool

**기능**:
- SQL 쿼리 실행
- 데이터 조회 및 분석
- 통계 정보 수집

**API**:
```python
class QueryTool:
    async def execute_sql(self, sql: str) -> QueryResult
    async def count_rows(self, table: str, where: str = None) -> int
    async def get_table_stats(self, table: str) -> TableStats
```

**사용 예**:
```
Agent: "conversation_sessions 테이블에 몇 개의 레코드가 있어?"
→ QueryTool.count_rows("conversation_sessions")
```

### 3.5 Validation Tool

**기능**:
- 테이블 존재 확인
- RPC 함수 존재 확인
- 데이터 무결성 검사
- RLS 정책 확인

**API**:
```python
class ValidationTool:
    async def table_exists(self, table: str) -> bool
    async def function_exists(self, name: str) -> bool
    async def check_foreign_keys(self, table: str) -> list[FKViolation]
    async def verify_rls(self, table: str) -> RLSStatus
```

---

## 4. Agent 프롬프트 설계

### System Prompt

```
당신은 Supabase PostgreSQL 데이터베이스 전문가입니다.

역할:
- Migration 실행 및 검증
- 테이블 스키마 관리
- RPC 함수 작성 및 테스트
- 데이터 조회 및 분석
- 성능 최적화 및 문제 해결

사용 가능한 도구:
1. run_migration(file_path) - Migration 실행
2. create_table(name, columns) - 테이블 생성
3. create_rpc(name, sql) - RPC 함수 생성
4. query_data(sql) - 데이터 조회
5. validate(target) - 검증

지침:
- 항상 안전한 작업 우선 (백업, 검증)
- 파괴적인 작업 전 사용자 확인
- 명확한 에러 메시지 제공
- 실행 결과 요약 제공
```

### 명령 예시 및 응답

| 사용자 명령 | Agent 동작 |
|------------|-----------|
| "Migration 007 실행해줘" | run_migration("migrations/007_*.sql") → 검증 → 결과 보고 |
| "conversation_sessions 테이블 구조 보여줘" | get_schema("conversation_sessions") → 포맷팅하여 출력 |
| "활성 세션이 몇 개야?" | query_data("SELECT COUNT(*) FROM conversation_sessions WHERE status='active'") |
| "만료된 세션 정리해줘" | test_function("cleanup_expired_sessions") → 결과 확인 |

---

## 5. CLI 인터페이스

### 사용 방법

```bash
# 대화형 모드
python scripts/supabase_agent_cli.py

# 단일 명령 실행
python scripts/supabase_agent_cli.py "Migration 007 실행해줘"

# Migration 특화
python scripts/supabase_agent_cli.py migrate 007

# 검증만
python scripts/supabase_agent_cli.py verify
```

### CLI 기능

```python
# scripts/supabase_agent_cli.py

async def main():
    agent = SupabaseAgent(ai_client, supabase_client)

    if len(sys.argv) > 1:
        # 단일 명령
        command = " ".join(sys.argv[1:])
        result = await agent.execute(command)
        print(result.message)
    else:
        # 대화형 모드
        print("Supabase Agent CLI")
        print("명령어 입력 (종료: exit)")

        while True:
            command = input("\n> ")
            if command.lower() in ["exit", "quit"]:
                break

            result = await agent.execute(command)
            print(f"\n{result.message}")
```

---

## 6. 구현 우선순위

### Phase 1: 기본 기능 (필수)
1. ✅ MigrationTool - Migration 실행 및 검증
2. ✅ ValidationTool - 테이블/함수 존재 확인
3. ✅ CLI 기본 구조
4. ✅ Agent 클래스 기본 구조

### Phase 2: 확장 기능
1. SchemaTool - 테이블/컬럼 관리
2. RPCTool - RPC 함수 관리
3. QueryTool - 데이터 조회

### Phase 3: 고급 기능
1. 성능 분석
2. 자동 인덱스 추천
3. RLS 정책 관리
4. 백업/복원

---

## 7. 안전장치

### 7.1 파괴적 작업 방지

```python
DESTRUCTIVE_OPERATIONS = [
    "DROP TABLE",
    "DROP DATABASE",
    "DELETE FROM",
    "TRUNCATE",
]

def require_confirmation(operation: str) -> bool:
    """파괴적 작업 전 확인"""
    if any(op in operation.upper() for op in DESTRUCTIVE_OPERATIONS):
        print(f"⚠️  경고: 파괴적 작업입니다!")
        print(f"   작업: {operation}")
        confirm = input("   계속하시겠습니까? (yes/no): ")
        return confirm.lower() == "yes"
    return True
```

### 7.2 Dry-Run 모드

```python
class SupabaseAgent:
    def __init__(self, ..., dry_run: bool = False):
        self.dry_run = dry_run

    async def execute(self, command: str):
        if self.dry_run:
            print(f"[DRY-RUN] {command}")
            return AgentResponse(success=True, message="Dry run - 실제 실행 안 함")
```

---

## 8. 사용 시나리오

### 시나리오 1: Migration 실행

```
User: Migration 007을 실행해줘

Agent: Migration 007을 실행하겠습니다.
       파일: migrations/007_add_conversation_tables.sql

       [실행 중...]

       ✅ 성공!

       생성된 테이블:
       - conversation_sessions
       - conversation_messages

       생성된 함수:
       - get_or_create_conversation_session
       - get_conversation_history
       - save_conversation_message
       - cleanup_expired_sessions
       - complete_conversation_session

       다음 단계:
       1. FORCE_CONVERSATION_MOCK=false 설정
       2. 서버 재시작
```

### 시나리오 2: 데이터 분석

```
User: 오늘 생성된 세션이 몇 개야?

Agent: 데이터를 조회하겠습니다.

       쿼리: SELECT COUNT(*) FROM conversation_sessions
             WHERE DATE(created_at) = CURRENT_DATE

       결과: 23개 세션

       상세:
       - 활성: 18개
       - 완료: 5개
       - 만료: 0개
```

### 시나리오 3: 문제 해결

```
User: get_conversation_history 함수가 작동 안 해

Agent: 함수를 검증하겠습니다.

       [검사 중...]

       ✅ 함수 존재: get_conversation_history
       ✅ 파라미터: p_session_id, p_limit

       테스트 실행:

       결과: 정상 작동

       반환값: 3개 메시지

       문제가 지속되면 에러 메시지를 공유해주세요.
```

---

## 9. 확장 가능성

### 9.1 다른 Agent와 연동

```python
# ChatService에서 SupabaseAgent 사용
class ChatService:
    def __init__(self, ..., supabase_agent: SupabaseAgent = None):
        self.supabase_agent = supabase_agent

    async def optimize_database(self):
        """대화 히스토리 최적화"""
        await self.supabase_agent.execute("만료된 세션 정리해줘")
        await self.supabase_agent.execute("인덱스 최적화 분석해줘")
```

### 9.2 자동화 작업

```python
# 정기 유지보수
async def daily_maintenance():
    agent = SupabaseAgent(...)

    await agent.execute("만료된 세션 정리")
    await agent.execute("30일 이상 된 메시지 아카이빙")
    await agent.execute("테이블 통계 업데이트")
    await agent.execute("느린 쿼리 분석")
```

---

## 10. 구현 체크리스트

### Phase 1 (기본)
- [ ] `src/shared/supabase_agent/__init__.py`
- [ ] `src/shared/supabase_agent/agent.py` - 메인 agent
- [ ] `src/shared/supabase_agent/tools/migration.py`
- [ ] `src/shared/supabase_agent/tools/validation.py`
- [ ] `src/shared/supabase_agent/prompts.py`
- [ ] `src/shared/supabase_agent/schemas.py`
- [ ] `scripts/supabase_agent_cli.py` - CLI
- [ ] 테스트: `tests/test_supabase_agent.py`

### Phase 2 (확장)
- [ ] `tools/schema.py`
- [ ] `tools/rpc.py`
- [ ] `tools/query.py`
- [ ] AI 명령 파싱 개선
- [ ] 에러 핸들링 강화

### Phase 3 (고급)
- [ ] 성능 분석 기능
- [ ] 백업/복원 기능
- [ ] RLS 정책 관리
- [ ] Web UI 인터페이스

---

## 11. 예상 효과

### 개발 생산성
- Migration 실행 시간: 5분 → 30초
- 검증 작업: 수동 → 자동
- 에러 디버깅: 시간 단축 50%

### 안전성
- 파괴적 작업 사전 차단
- 자동 검증으로 실수 방지
- 명확한 롤백 경로

### 유지보수
- 자연어 명령으로 쉬운 관리
- 일관된 작업 방식
- 지식 공유 용이

---

**작성일**: 2026-03-20
**작성자**: Claude Code Agent
**상태**: 설계 완료, 구현 대기
