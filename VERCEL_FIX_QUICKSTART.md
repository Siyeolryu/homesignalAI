# Vercel ValidationError - 빠른 해결 가이드

**작성일:** 2026-03-18
**상태:** ✅ 코드 수정 완료 → 📋 환경변수 설정 필요

---

## 🎯 즉시 실행 체크리스트

### 1단계: Vercel CLI 설치 (5분) ⚠️ 필수

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login

# 프로젝트 연결
cd D:\Ai_project\home_signal_ai
vercel link
```

### 2단계: 환경변수 설정 (5분) ⚠️ 필수

**Option A: CLI로 설정 (권장)**

```bash
# Production 환경변수 추가
vercel env add SUPABASE_URL production
# 입력: <your-supabase-project-url>

vercel env add SUPABASE_KEY production
# 입력: <your-supabase-anon-key>

vercel env add SUPABASE_SERVICE_ROLE_KEY production
# 입력: <your-supabase-service-role-key>

vercel env add ANTHROPIC_API_KEY production
# 입력: <your-anthropic-api-key>

vercel env add AI_PROVIDER production
# 입력: anthropic

vercel env add APP_ENV production
# 입력: production

vercel env add DEBUG production
# 입력: false
```

**Option B: Vercel Dashboard로 설정**

1. https://vercel.com/dashboard 접속
2. 프로젝트 선택
3. Settings → Environment Variables
4. 다음 변수들을 **Production, Preview, Development** 모두 체크하여 추가:

| Variable | Value |
|----------|-------|
| SUPABASE_URL | `https://yietqoikdaqpwmmvamtv.supabase.co` |
| SUPABASE_KEY | `.env` 파일의 anon key |
| SUPABASE_SERVICE_ROLE_KEY | `.env` 파일의 service role key |
| ANTHROPIC_API_KEY | `.env` 파일의 Anthropic key |
| AI_PROVIDER | `anthropic` |
| APP_ENV | `production` |
| DEBUG | `false` |

### 3단계: 재배포 (2분) ⚠️ 필수

```bash
# 재배포 (환경변수 적용)
vercel --prod --force
```

또는 Vercel Dashboard에서:
- Deployments 탭 → 최신 배포 → Redeploy 버튼 클릭

### 4단계: 검증 (1분)

```bash
# Health check
curl https://your-vercel-url.vercel.app/health

# 예상 응답:
{
  "status": "healthy",
  "app_env": "production",
  "supabase_url": "https://yietqoikdaqpwmmvamtv.supabase.co"
}
```

---

## ✅ 완료된 코드 수정 사항

### 1. `src/config/settings.py` 개선
- ✅ `field_validator` 추가하여 빈 문자열 처리
- ✅ `str_strip_whitespace=True` 설정 추가
- ✅ 빈 문자열("")을 None으로 변환하여 placeholder 트리거

### 2. `api/index.py` 개선
- ✅ `ensure_env_var()` 함수 추가
- ✅ 빈 문자열 명시적 체크 (`value.strip() == ""`)
- ✅ `setdefault` 대신 직접 설정으로 변경

### 3. 문서 및 도구 생성
- ✅ 상세 문제 분석 보고서: `docs/VERCEL_VALIDATION_ERROR_FIX_2026-03-18.md`
- ✅ 환경변수 검증 스크립트: `scripts/verify_vercel_env.py`
- ✅ 설정 테스트 스크립트: `scripts/test_settings_fallback.py`

---

## 🔍 문제 원인 요약

### 근본 원인
1. **Vercel Dashboard에 환경변수 미설정**
2. Pydantic이 빈 값을 받으면 ValidationError 발생
3. `model_validator(mode="after")`는 검증 후 실행되어 이미 늦음

### 해결 방법
1. **환경변수 설정** (위 2단계)
2. **field_validator(mode="before")** 추가로 검증 전 처리
3. **api/index.py**에서 빈 문자열 명시적 체크

---

## 📊 검증 스크립트 사용법

### 로컬 환경변수 확인
```bash
uv run python scripts/verify_vercel_env.py --local
```

### Vercel 환경변수 확인 (CLI 필요)
```bash
uv run python scripts/verify_vercel_env.py --vercel production
```

### .env 파일 확인
```bash
uv run python scripts/verify_vercel_env.py --env-file
```

### 모든 검증 실행
```bash
uv run python scripts/verify_vercel_env.py --all
```

---

## 🚨 주의사항

### Vercel CLI 없을 때
- Vercel Dashboard 웹 UI로 환경변수 설정 (Option B)
- CLI 설치 권장: `npm install -g vercel`

### 환경변수 값 복사 시
- **따옴표 제거**: `"value"` → `value`
- **공백 제거**: 앞뒤 공백 없이
- **전체 복사**: API 키는 전체 문자열 복사

### 재배포 필수
- 환경변수 추가/수정 후 **반드시 재배포** 필요
- Redeploy 버튼 클릭 또는 `vercel --prod --force`

---

## 📚 상세 문서

- **상세 분석**: `docs/VERCEL_VALIDATION_ERROR_FIX_2026-03-18.md`
- **환경변수 가이드**: `docs/VERCEL_ENV_SETUP.md`
- **Vercel 아키텍처**: `docs/08_Vercel_Architecture_Guide.md`

---

## 💬 문제 지속 시

### 1. Function Logs 확인
```
Vercel Dashboard → Deployments → 최신 배포 → Function Logs
```

### 2. 환경변수 재확인
```bash
vercel env ls production
```

### 3. 강제 재배포
```bash
vercel env rm SUPABASE_URL production
vercel env add SUPABASE_URL production
vercel --prod --force
```

### 4. 긴급 연락처
- Vercel Support: https://vercel.com/support
- GitHub Issues: https://github.com/anthropics/claude-code/issues

---

**최종 업데이트:** 2026-03-18
**다음 단계:** 환경변수 설정 → 재배포 → Health Check ✅
