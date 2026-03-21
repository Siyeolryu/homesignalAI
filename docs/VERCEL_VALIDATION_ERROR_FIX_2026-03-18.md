# Vercel ValidationError 해결 보고서

**작성일:** 2026-03-18
**심각도:** P0 - Critical
**상태:** 🔍 분석 완료 → ✅ 해결 진행 중
**담당:** Vercel 전문가 + Claude Code Expert

---

## 📋 Executive Summary

### 문제 개요
Vercel 배포 환경에서 FastAPI 애플리케이션 초기화 시 Pydantic ValidationError 발생으로 인한 서비스 장애

### 에러 메시지
```python
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
supabase_url
  Field required [type=missing, input_value={}, input_type=dict]
supabase_key
  Field required [type=missing, input_value={}, input_type=dict]
```

### 근본 원인 분석
1. **환경변수 누락**: Vercel Dashboard에 환경변수가 설정되지 않음
2. **Import 체인 문제**: `settings.py`가 모듈 레벨에서 lazy loading을 구현했으나, 실제로는 `from src.config import settings` 호출 시 `__getattr__`이 즉시 `get_settings()` 호출
3. **Vercel 런타임 타이밍**: Python 런타임 초기화 시점에 환경변수가 완전히 로드되지 않았을 가능성

---

## 🔴 상세 에러 분석

### 1. 에러 발생 지점 (Call Stack)

```
FUNCTION_INVOCATION_FAILED
└─► /var/task/api/index.py (Vercel Entry Point)
    ├─► import sys, os (환경변수 setdefault 설정)
    └─► from src.main import app
        └─► src/main.py:15
            └─► from src.chat import router as chat_router
                └─► src/chat/router.py:3
                    └─► from src.shared.ai_client import get_ai_client
                        └─► src/shared/ai_client.py:8
                            └─► from src.config import settings
                                └─► src/config/settings.py:220 (__getattr__)
                                    └─► return get_settings()
                                        └─► Settings().__init__()
                                            └─► Pydantic validation
                                                └─► ❌ ValidationError
```

### 2. 코드 분석

#### api/index.py (Entry Point)
```python
# Line 19-27: 환경변수 기본값 설정
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "placeholder-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "placeholder-service-key")

# Line 64: FastAPI app import
from src.main import app  # ❌ 이 시점에 에러 발생
```

**분석:**
- `os.environ.setdefault()`는 환경변수가 **없을 때만** 설정
- Vercel에서 환경변수가 빈 문자열("")로 설정되어 있으면 setdefault가 작동하지 않음
- 환경변수가 아예 없거나, 빈 값으로 설정된 경우 문제 발생

#### src/config/settings.py (Settings Configuration)
```python
# Line 26-28: Optional 필드 정의
supabase_url: str | None = None
supabase_key: str | None = None
supabase_service_role_key: str | None = None

# Line 58-106: model_validator로 기본값 설정
@model_validator(mode="after")
def set_required_defaults(self) -> "Settings":
    if not self.supabase_url:
        self.supabase_url = "https://placeholder.supabase.co"
        logger.warning("SUPABASE_URL 환경변수가 설정되지 않아 placeholder로 초기화됨.")
    # ...
```

**분석:**
- 필드는 Optional로 정의되어 있음 (`str | None = None`)
- `model_validator`로 None 값 감지 후 placeholder 설정
- **그런데 왜 ValidationError가 발생하는가?**

### 3. 근본 원인 (Root Cause Analysis)

#### 원인 A: Pydantic의 환경변수 처리 로직
Pydantic Settings는 다음 순서로 값을 로드:
1. 환경변수 조회 (`os.getenv("SUPABASE_URL")`)
2. `.env` 파일 조회 (Vercel에는 없음)
3. 필드 기본값 사용 (`None`)

**문제:**
- Vercel에서 환경변수가 **빈 문자열("")**로 설정되면, Pydantic은 이를 **"값이 있음"**으로 간주
- 빈 문자열은 `str` 타입으로 간주되지만, **내부 검증 로직**에서 실패할 수 있음
- `model_validator(mode="after")`는 필드 검증 **이후**에 실행되므로, 이미 에러가 발생한 후

#### 원인 B: Vercel Dashboard 환경변수 미설정
가장 가능성 높은 원인:
```bash
# Vercel Dashboard에서 환경변수가 아예 설정되지 않음
SUPABASE_URL: (설정되지 않음)
SUPABASE_KEY: (설정되지 않음)
```

결과:
- `os.getenv("SUPABASE_URL")` → `None`
- Pydantic은 `input_value={}`로 표시 (빈 딕셔너리)
- 필드 검증에서 "Field required" 에러 발생

#### 원인 C: settings.py의 모듈 레벨 초기화
```python
# Line 220-222: __getattr__ lazy loading
def __getattr__(name: str) -> Settings:
    if name == "settings":
        return get_settings()  # ❌ 즉시 실행
```

**문제:**
- `from src.config import settings` 호출 시 `__getattr__`이 즉시 실행
- `get_settings()` → `Settings()` → Pydantic 검증 → 에러
- **api/index.py에서 setdefault 설정 후에도**, 이미 import 체인이 시작되면 타이밍 문제 발생 가능

---

## 🔍 진단 결과

### 환경변수 상태 확인

에러 로그에서 확인된 환경변수 상태:
```
[Vercel] Environment Variables Check:
  - SUPABASE_URL: ✗ MISSING
  - SUPABASE_KEY: ✗ MISSING
  - SUPABASE_SERVICE_ROLE_KEY: ✗ MISSING
  - OPENAI_API_KEY: ✗ MISSING
  - APP_ENV: NOT SET
  - DEBUG: NOT SET
```

**결론:** Vercel Dashboard에 환경변수가 전혀 설정되지 않음

### Pydantic 검증 실패 원인
```python
# Pydantic이 받은 input
input_value={}  # 빈 딕셔너리

# 이유:
# 1. 환경변수 없음 → os.getenv() → None
# 2. .env 파일 없음 (Vercel 환경)
# 3. pydantic-settings가 빈 dict를 source로 전달
# 4. 필드 검증: supabase_url는 Optional이지만, model_config 설정에 의해 required로 간주될 수 있음
```

---

## ✅ 해결 방안

### Solution 1: Vercel Dashboard 환경변수 설정 (필수)

#### 방법 A: Vercel CLI 사용
```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. 로그인
vercel login

# 3. 프로젝트 연결
cd D:\Ai_project\home_signal_ai
vercel link

# 4. 환경변수 설정
vercel env add SUPABASE_URL production
# 입력: https://yietqoikdaqpwmmvamtv.supabase.co

vercel env add SUPABASE_KEY production
# 입력: eyJhbGci... (anon key)

vercel env add SUPABASE_SERVICE_ROLE_KEY production
# 입력: eyJhbGci... (service_role key)

vercel env add OPENAI_API_KEY production
# 입력: (비어있으면 스킵)

vercel env add ANTHROPIC_API_KEY production
# 입력: sk-ant-...

vercel env add AI_PROVIDER production
# 입력: anthropic

vercel env add APP_ENV production
# 입력: production

vercel env add DEBUG production
# 입력: false

# 5. 재배포
vercel --prod --force
```

#### 방법 B: Vercel Dashboard 웹 UI
1. https://vercel.com/dashboard 접속
2. 프로젝트 선택 (homesignal-ai 또는 backend 프로젝트)
3. **Settings** → **Environment Variables**
4. 다음 변수 추가:

| Variable Name | Value | Environments |
|---------------|-------|--------------|
| `SUPABASE_URL` | `https://yietqoikdaqpwmmvamtv.supabase.co` | Production, Preview, Development |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Production, Preview, Development |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | Production, Preview, Development |
| `AI_PROVIDER` | `anthropic` | Production, Preview, Development |
| `APP_ENV` | `production` | Production |
| `APP_ENV` | `development` | Preview, Development |
| `DEBUG` | `false` | Production |
| `DEBUG` | `true` | Preview, Development |

5. **Redeploy** 버튼 클릭

#### 방법 C: 자동화 스크립트 (CLI 설치 후)
```bash
# Vercel CLI 설치 후 실행
uv run python scripts/setup_vercel_env.py --environment production

# Dry-run으로 테스트
uv run python scripts/setup_vercel_env.py --dry-run
```

### Solution 2: settings.py 개선 (추가 안전장치)

현재 `settings.py`는 이미 fallback 로직이 있지만, Pydantic 검증 타이밍 문제를 해결하기 위해 추가 개선:

#### Option A: 필드를 완전히 Optional로 변경 + 기본값 즉시 설정
```python
# src/config/settings.py
class Settings(BaseSettings):
    # CRITICAL: 기본값을 필드 정의 시점에 설정
    supabase_url: str = "https://placeholder.supabase.co"
    supabase_key: str = "placeholder-key"
    supabase_service_role_key: str = "placeholder-service-key"

    # model_validator는 production 경고용으로만 사용
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env == "production":
            if "placeholder" in self.supabase_url:
                logger.critical("🚨 Production에서 placeholder Supabase URL 사용 중!")
        return self
```

#### Option B: 환경변수 강제 설정 (api/index.py 개선)
```python
# api/index.py - Line 19-27 개선
import os

# CRITICAL: setdefault 대신 직접 설정 (빈 문자열 케이스 방지)
if not os.environ.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL") == "":
    os.environ["SUPABASE_URL"] = "https://placeholder.supabase.co"

if not os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY") == "":
    os.environ["SUPABASE_KEY"] = "placeholder-key"

if not os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") == "":
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "placeholder-service-key"

if not os.environ.get("APP_ENV"):
    os.environ["APP_ENV"] = "production"

if not os.environ.get("DEBUG"):
    os.environ["DEBUG"] = "false"
```

#### Option C: Pydantic Settings Config 조정
```python
# src/config/settings.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
        validate_default=False,
        # CRITICAL: 환경변수 우선순위 명시
        env_prefix="",
        # 빈 값을 None으로 처리
        str_strip_whitespace=True,
    )

    # 필드에 validator 추가
    @field_validator("supabase_url", mode="before")
    @classmethod
    def validate_supabase_url(cls, v):
        if not v or v == "":
            return "https://placeholder.supabase.co"
        return v

    @field_validator("supabase_key", mode="before")
    @classmethod
    def validate_supabase_key(cls, v):
        if not v or v == "":
            return "placeholder-key"
        return v
```

### Solution 3: 긴급 Hot Fix (임시 조치)

Vercel Dashboard 접속이 불가능하거나 즉시 해결이 필요한 경우:

```python
# src/config/settings.py - get_settings() 함수 수정
@lru_cache
def get_settings() -> Settings:
    global _settings
    if _settings is not None:
        return _settings

    try:
        # 환경변수 강제 설정 (Vercel 런타임에서 누락 대비)
        import os
        if not os.getenv("SUPABASE_URL"):
            os.environ["SUPABASE_URL"] = "https://placeholder.supabase.co"
        if not os.getenv("SUPABASE_KEY"):
            os.environ["SUPABASE_KEY"] = "placeholder-key"
        if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
            os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "placeholder-service-key"

        _settings = Settings()
        return _settings
    except Exception as e:
        # 이미 있는 fallback 로직...
```

---

## 🔧 구현 계획

### Phase 1: 즉시 조치 (Emergency Fix) ✅

1. **Vercel Dashboard 환경변수 설정**
   - [ ] Vercel Dashboard 접속
   - [ ] 환경변수 8개 추가 (위 표 참조)
   - [ ] Production, Preview, Development 모두 체크
   - [ ] Save

2. **재배포**
   - [ ] Vercel Dashboard → Deployments → Redeploy
   - [ ] 또는 `vercel --prod --force` (CLI 설치 시)

### Phase 2: 코드 개선 (Long-term Fix) 🔄

1. **settings.py 개선**
   - [ ] 필드 validator 추가 (`@field_validator("supabase_url", mode="before")`)
   - [ ] 빈 문자열 케이스 처리
   - [ ] 테스트 코드 추가

2. **api/index.py 개선**
   - [ ] `setdefault` → 직접 설정으로 변경
   - [ ] 빈 문자열 체크 로직 추가

3. **검증 스크립트 작성**
   - [ ] `scripts/verify_vercel_env.py` 생성
   - [ ] 배포 전 환경변수 검증 자동화

### Phase 3: 문서화 및 모니터링 📝

1. **배포 가이드 업데이트**
   - [ ] `docs/VERCEL_ENV_SETUP.md` 업데이트
   - [ ] `CLAUDE.md` Troubleshooting 섹션 추가

2. **CI/CD 체크**
   - [ ] GitHub Actions에 환경변수 검증 추가
   - [ ] Pre-deployment validation hook

---

## 📊 검증 방법

### 1. 로컬 검증 (환경변수 없이 실행)
```bash
# 환경변수 제거 후 테스트
unset SUPABASE_URL SUPABASE_KEY SUPABASE_SERVICE_ROLE_KEY OPENAI_API_KEY

# FastAPI 실행
uv run uvicorn src.main:app --reload

# 예상 결과: placeholder로 정상 실행, 경고 로그 출력
```

### 2. Vercel 배포 후 검증
```bash
# Health check
curl https://your-app.vercel.app/health

# 예상 응답
{
  "status": "healthy",
  "app_env": "production",
  "supabase_url": "https://yietqoikdaqpwmmvamtv.supabase.co",  # placeholder 아님
  "timestamp": "2026-03-18T..."
}
```

### 3. Function Logs 확인
```
[Vercel] Environment Variables Check:
  - SUPABASE_URL: ✓ SET
  - SUPABASE_KEY: ✓ SET
  - SUPABASE_SERVICE_ROLE_KEY: ✓ SET
  - OPENAI_API_KEY: ✗ MISSING (optional)
  - APP_ENV: production
  - DEBUG: false
```

---

## 🎯 우선순위 액션

### 즉시 실행 (P0)
1. ✅ **Vercel Dashboard 환경변수 설정** (5분)
   - SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY, ANTHROPIC_API_KEY
2. ✅ **재배포** (2분)
   - Redeploy 버튼 클릭 또는 `vercel --prod --force`
3. ✅ **Health check 확인** (1분)
   - `curl https://your-app.vercel.app/health`

### 단기 실행 (P1)
4. 🔄 **settings.py field validator 추가** (30분)
5. 🔄 **api/index.py 빈 문자열 처리 개선** (15분)
6. 📝 **검증 스크립트 작성** (1시간)

### 중기 실행 (P2)
7. 📝 **문서 업데이트** (1시간)
8. 🔄 **CI/CD 환경변수 검증 추가** (2시간)

---

## 💡 교훈 및 Best Practices

### 1. Vercel 환경변수 설정은 필수
- **모든 환경**에 설정: Production, Preview, Development
- **빈 문자열 금지**: 값이 없으면 아예 설정하지 않거나, 명시적 기본값 사용
- **민감 정보 분리**: Service Role Key는 백엔드만, Anon Key는 프론트엔드 가능

### 2. Pydantic Settings 방어적 프로그래밍
- **Optional 필드에도 기본값** 설정
- **field_validator(mode="before")** 사용하여 빈 값 처리
- **model_validator(mode="after")** 사용하여 일관성 검증

### 3. Vercel Serverless 특성 이해
- **Cold Start**: 첫 요청 시 모듈 로딩 → 환경변수 준비 완료 전에 import 가능
- **Module-level 초기화 최소화**: Lazy loading 패턴 사용
- **Emergency Fallback**: api/index.py에서 환경변수 강제 설정

### 4. 배포 전 체크리스트
```bash
# 1. 환경변수 확인
vercel env ls production

# 2. 로컬 빌드 테스트 (환경변수 없이)
unset SUPABASE_URL && uv run uvicorn src.main:app --reload

# 3. 환경변수 검증 스크립트
uv run python scripts/validate_env.py --strict

# 4. 배포
vercel --prod

# 5. Health check
curl https://your-app.vercel.app/health
```

---

## 📚 참고 자료

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/fastapi)
- [HomeSignal AI Vercel Architecture Guide](./08_Vercel_Architecture_Guide.md)
- [Vercel Environment Setup Guide](./VERCEL_ENV_SETUP.md)

---

## 📞 연락처 및 지원

**긴급 문의:** Vercel Dashboard Support
**문서 업데이트:** @DevOps-Team
**코드 리뷰:** @Backend-Lead

---

**보고서 작성:** 2026-03-18
**다음 리뷰:** 환경변수 설정 완료 후
**최종 목표:** 모든 환경에서 안정적인 Vercel 배포
