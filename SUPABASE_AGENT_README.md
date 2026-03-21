# Supabase Agent 사용 가이드

## ✅ 구현 완료

Supabase 데이터베이스를 자연어 명령으로 관리하는 전문 Agent가 구현되었습니다!

---

## 주요 기능

### Phase 1 (구현 완료)
- ✅ **Migration 실행**: SQL 파일 자동 실행 및 검증
- ✅ **테이블 검증**: 테이블 존재 확인
- ✅ **함수 검증**: RPC 함수 존재 확인
- ✅ **데이터 조회**: 간단한 개수 조회
- ✅ **CLI 인터페이스**: 대화형 & 단일 명령 모드
- ✅ **Dry-run 모드**: 안전한 테스트

### Phase 2 (TODO)
- [ ] 스키마 관리 (테이블/컬럼 생성)
- [ ] RPC 함수 작성
- [ ] 고급 데이터 조회

---

## 사용법

### 1. 대화형 모드

```bash
python scripts/supabase_agent_cli.py
```

**출력**:
```
================================================================================
Supabase Agent CLI
================================================================================

명령어 예시:
  - Migration 007 실행해줘
  - conversation_sessions 테이블 확인해줘
  - 활성 세션 개수 알려줘
  - exit (종료)

> Migration 007 실행해줘

✅ Migration 007 실행 완료!

파일: migrations/007_add_conversation_tables.sql

생성된 테이블 (2개):
  - conversation_sessions
  - conversation_messages

생성된 함수 (5개):
  - get_or_create_conversation_session()
  - get_conversation_history()
  - save_conversation_message()
  - cleanup_expired_sessions()
  - complete_conversation_session()

실행 시간: 1.23초

다음 단계:
  1. 검증: python verify_migration_007.py
  2. FORCE_CONVERSATION_MOCK=false 설정
  3. 서버 재시작
```

### 2. 단일 명령 모드

```bash
# 일반 명령
python scripts/supabase_agent_cli.py "Migration 007 실행해줘"

# 단축 명령
python scripts/supabase_agent_cli.py migrate 007

# 검증
python scripts/supabase_agent_cli.py verify
```

### 3. Dry-run 모드 (안전)

```bash
python scripts/supabase_agent_cli.py --dry-run "Migration 007 실행해줘"
```

**출력**:
```
[INFO] Dry-run 모드 활성화 (실제 실행하지 않음)

[DRY-RUN] Migration 007 실행해줘
(실제 실행하지 않음)
```

---

## 지원하는 명령

### Migration 관리

| 명령 | 설명 |
|------|------|
| `Migration 007 실행해줘` | Migration 007 실행 |
| `Migration 7 실행해줘` | Migration 007 실행 (자동 변환) |
| `migrate 007` | 단축 명령 |

### 검증

| 명령 | 설명 |
|------|------|
| `conversation_sessions 테이블 확인해줘` | 테이블 존재 확인 |
| `get_conversation_history 함수 확인해줘` | RPC 함수 존재 확인 |
| `Migration 007 검증해줘` | Migration 검증 |

### 데이터 조회

| 명령 | 설명 |
|------|------|
| `활성 세션 개수 알려줘` | conversation_sessions (status=active) 개수 |
| `세션 개수 알려줘` | conversation_sessions 전체 개수 |

---

## 아키텍처

### 파일 구조

```
src/shared/supabase_agent/
├── __init__.py
├── agent.py                 # 메인 agent 클래스
├── schemas.py               # Pydantic 스키마
├── prompts.py               # Agent 프롬프트
└── tools/
    ├── __init__.py
    ├── migration.py         # Migration 도구
    └── validation.py        # 검증 도구

scripts/
└── supabase_agent_cli.py    # CLI 인터페이스

tests/
└── test_supabase_agent.py   # 테스트
```

### 클래스 다이어그램

```
SupabaseAgent
├── MigrationTool
│   ├── run_migration()
│   ├── list_migrations()
│   └── find_migration()
├── ValidationTool
│   ├── table_exists()
│   ├── function_exists()
│   ├── validate_migration()
│   └── count_rows()
└── AIClient (선택사항)
```

---

## 실제 사용 예시

### 예시 1: Migration 007 실행

```bash
$ python scripts/supabase_agent_cli.py

> Migration 007 실행해줘

✅ Migration 007 실행 완료!

파일: migrations/007_add_conversation_tables.sql

생성된 테이블 (2개):
  - conversation_sessions
  - conversation_messages

생성된 함수 (5개):
  - get_or_create_conversation_session()
  - get_conversation_history()
  - save_conversation_message()
  - cleanup_expired_sessions()
  - complete_conversation_session()

실행 시간: 1.45초

다음 단계:
  1. 검증: python verify_migration_007.py
  2. FORCE_CONVERSATION_MOCK=false 설정
  3. 서버 재시작
```

### 예시 2: 검증

```bash
> conversation_sessions 테이블 확인해줘

✅ 테이블 'conversation_sessions'이(가) 존재합니다.
```

### 예시 3: 데이터 조회

```bash
> 활성 세션 개수 알려줘

📊 conversation_sessions 테이블 (status=active): 23개
```

---

## Python API 사용

### 기본 사용

```python
from src.shared.database import get_supabase_client
from src.shared.supabase_agent import SupabaseAgent

# Supabase 클라이언트
supabase = get_supabase_client(use_service_role=True)

# Agent 초기화
agent = SupabaseAgent(supabase_client=supabase)

# 명령 실행
response = await agent.execute("Migration 007 실행해줘")

print(response.message)
print(response.data)
```

### Dry-run 모드

```python
# 안전한 테스트 (실제 실행 안 함)
agent = SupabaseAgent(supabase_client=supabase, dry_run=True)

response = await agent.execute("Migration 007 실행해줘")
# [DRY-RUN] Migration 007 실행해줘
```

### 도구 직접 사용

```python
from src.shared.supabase_agent.tools import MigrationTool, ValidationTool

# Migration 도구
migration_tool = MigrationTool(supabase)
result = await migration_tool.run_migration("migrations/007_add_conversation_tables.sql")

print(f"생성된 테이블: {result.tables_created}")
print(f"생성된 함수: {result.functions_created}")

# 검증 도구
validation_tool = ValidationTool(supabase)
exists = await validation_tool.table_exists("conversation_sessions")
print(f"테이블 존재: {exists.exists}")
```

---

## 테스트

### 단위 테스트

```bash
# 전체 테스트
pytest tests/test_supabase_agent.py

# 특정 테스트
pytest tests/test_supabase_agent.py::TestSupabaseAgent::test_dry_run_mode -v
```

### 간단 테스트

```bash
python test_supabase_agent.py
```

**출력**:
```
================================================================================
Supabase Agent 테스트
================================================================================

[OK] Agent 초기화 (Dry-run 모드)

[테스트 1] Migration 007 실행해줘
--------------------------------------------------------------------------------
결과: [OK]
[DRY-RUN] Migration 007 실행해줘
(실제 실행하지 않음)

[테스트 2] conversation_sessions 테이블 확인해줘
--------------------------------------------------------------------------------
결과: [OK]
[DRY-RUN] conversation_sessions 테이블 확인해줘
(실제 실행하지 않음)

[테스트 3] 활성 세션 개수 알려줘
--------------------------------------------------------------------------------
결과: [OK]
[DRY-RUN] 활성 세션 개수 알려줘
(실제 실행하지 않음)

================================================================================
테스트 완료
================================================================================
```

---

## 안전장치

### 1. Dry-run 모드
- `--dry-run` 플래그로 실제 실행 없이 테스트
- 명령 분석 및 도구 선택만 수행

### 2. 파괴적 작업 방지
- DROP, DELETE, TRUNCATE 명령 감지
- 사용자 확인 필요 (TODO)

### 3. 에러 핸들링
- 명확한 에러 메시지
- Migration 실패 시 롤백 안내

---

## 확장 계획

### Phase 2: 스키마 관리
- [ ] 테이블 생성/수정/삭제
- [ ] 컬럼 추가/수정/삭제
- [ ] 인덱스 생성/삭제

### Phase 3: RPC 함수 관리
- [ ] 함수 작성 지원
- [ ] 함수 테스트
- [ ] 함수 목록 조회

### Phase 4: 고급 기능
- [ ] AI 기반 명령 파싱
- [ ] 자동 백업/복원
- [ ] 성능 분석
- [ ] RLS 정책 관리

---

## 문제 해결

### 오류: "Could not find the function"
→ Migration이 실행되지 않았습니다. `Migration 007 실행해줘` 명령 실행

### 오류: "psycopg 모듈이 설치되지 않았습니다"
```bash
uv pip install psycopg
```

### 오류: "DATABASE_URL이 설정되지 않았습니다"
→ `.env` 파일에 `DATABASE_URL` 추가

### 네트워크 연결 오류
→ Supabase SQL Editor에서 수동 실행 (MIGRATION_007_GUIDE.md 참고)

---

## 참고 문서

- **설계 문서**: `docs/Supabase_Agent_Plan.md`
- **Migration 가이드**: `MIGRATION_007_GUIDE.md`
- **검증 보고서**: `VERIFICATION_REPORT.md`

---

**작성일**: 2026-03-20
**버전**: 1.0.0 (Phase 1)
**상태**: ✅ 기본 기능 구현 완료
