# Vercel FUNCTION_INVOCATION_FAILED 해결 가이드

## 🔴 현재 문제

https://homesignal-ai.vercel.app/ 에서 **500 FUNCTION_INVOCATION_FAILED** 에러 발생

**원인:** Vercel 환경변수가 설정되지 않아 Python 앱 초기화 실패

---

## ✅ 즉시 해결 방법

### Step 1: Vercel 환경변수 확인

```bash
# Vercel CLI로 현재 설정된 환경변수 확인
uv run python scripts/check_vercel_env.py
```

**예상 결과:**
```
❌ 누락된 환경변수 발견
  - SUPABASE_URL: Supabase 프로젝트 URL
  - SUPABASE_KEY: Supabase anon/public key
  - OPENAI_API_KEY: OpenAI API key
```

---

### Step 2: 환경변수 설정 (3가지 방법 중 선택)

#### 방법 A: 자동 설정 스크립트 (권장)

```bash
# .env 파일을 읽어 Vercel에 자동 업로드
uv run python scripts/setup_vercel_env.py --environment production

# 테스트 모드 (실제로 설정하지 않음)
uv run python scripts/setup_vercel_env.py --dry-run
```

#### 방법 B: Vercel CLI 수동 설정

```bash
# 각 환경변수를 하나씩 설정
vercel env add SUPABASE_URL production
# 값 입력: https://yietqoikdaqpwmmvamtv.supabase.co

vercel env add SUPABASE_KEY production
# 값 입력: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

vercel env add SUPABASE_SERVICE_ROLE_KEY production
# 값 입력: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

vercel env add OPENAI_API_KEY production
# 값 입력: sk-proj-...
```

#### 방법 C: Vercel Dashboard 설정

1. https://vercel.com/dashboard 접속
2. **homesignal-ai** 프로젝트 선택
3. **Settings** → **Environment Variables**
4. 다음 환경변수 추가 (Environment: Production):

| Key | Value | 설명 |
|-----|-------|------|
| `SUPABASE_URL` | `https://yietqoikdaqpwmmvamtv.supabase.co` | Supabase URL |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Service role key |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI API key |
| `APP_ENV` | `production` | 앱 환경 |
| `DEBUG` | `false` | 디버그 모드 |

**주의:** `.env` 파일에 실제 키가 있으면 그 값을 복사하세요.

---

### Step 3: 환경변수 재확인

```bash
# 설정 확인
vercel env ls production

# 또는
uv run python scripts/check_vercel_env.py
```

**예상 결과:**
```
✅ 모든 필수 환경변수가 설정되었습니다
```

---

### Step 4: 재배포

```bash
# 강제 재배포 (환경변수 적용)
vercel --prod --force
```

**배포 완료 후 URL 확인:**
```
✔ Production: https://homesignal-ai.vercel.app [복사됨]
```

---

### Step 5: 배포 확인

```bash
# Health check 엔드포인트 호출
curl https://homesignal-ai.vercel.app/health

# 또는 브라우저에서 접속
# https://homesignal-ai.vercel.app/health
```

**성공 시 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-14T...",
  "version": "0.1.0"
}
```

**실패 시 (Fallback 모드):**
```json
{
  "status": "error",
  "message": "Application failed to initialize",
  "env_check": {
    "SUPABASE_URL": "missing",
    "SUPABASE_KEY": "missing"
  }
}
```

→ **Fallback 응답이 나오면** Step 2로 돌아가서 환경변수를 다시 설정하세요.

---

## 🔍 Vercel 로그 확인

배포 후에도 에러가 발생하면 Vercel 로그를 확인하세요:

### 방법 1: Vercel Dashboard
1. https://vercel.com/dashboard
2. **homesignal-ai** 프로젝트 선택
3. **Deployments** 탭에서 최신 배포 클릭
4. **Logs** 탭에서 런타임 로그 확인

### 방법 2: Vercel CLI
```bash
# 실시간 로그 스트리밍
vercel logs homesignal-ai --follow

# 최근 100줄
vercel logs homesignal-ai --limit 100
```

**로그에서 확인할 내용:**
```
[Vercel] Environment variables check:
  SUPABASE_URL: ✓ Set
  SUPABASE_KEY: ✓ Set
  OPENAI_API_KEY: ✓ Set
[Vercel] ✓ FastAPI app loaded successfully
```

---

## 🛡️ 적용된 개선 사항

이번 업데이트로 다음이 개선되었습니다:

### 1. Settings 클래스 안전 초기화 (`src/config/settings.py`)
```python
@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        # 환경변수 없어도 크래시 방지
        logging.warning(f"Settings 초기화 경고: {e}")
        os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
        os.environ.setdefault("SUPABASE_KEY", "placeholder-key")
        return Settings()
```

### 2. API 엔트리포인트 에러 핸들링 (`api/index.py`)
- 환경변수 상태 로깅 추가
- 앱 로딩 실패 시 Fallback 앱 제공
- 에러 상세 정보 반환

### 3. 환경변수 확인 스크립트 (`scripts/check_vercel_env.py`)
- Vercel CLI를 통한 환경변수 확인
- 누락된 변수 자동 탐지

### 4. 자동 설정 스크립트 (`scripts/setup_vercel_env.py`)
- `.env` → Vercel 자동 업로드
- Dry-run 모드 지원

---

## 📋 체크리스트

배포 전 확인사항:

- [ ] Vercel CLI 설치 및 로그인 (`npm i -g vercel && vercel login`)
- [ ] 로컬 `.env` 파일에 실제 키 설정
- [ ] Vercel 환경변수 확인 (`uv run python scripts/check_vercel_env.py`)
- [ ] 누락된 환경변수 설정 (방법 A/B/C 중 택1)
- [ ] 재배포 (`vercel --prod --force`)
- [ ] Health check 확인 (`curl https://homesignal-ai.vercel.app/health`)
- [ ] Vercel 로그에서 에러 없는지 확인

---

## 🆘 문제가 해결되지 않으면

1. **Vercel 환경변수 삭제 후 재설정**
   ```bash
   vercel env rm SUPABASE_URL production
   vercel env add SUPABASE_URL production
   ```

2. **프로젝트 재연결**
   ```bash
   vercel link --yes
   vercel --prod
   ```

3. **로컬에서 환경변수 검증**
   ```bash
   uv run python scripts/validate_env.py --strict
   ```

4. **Vercel 프로젝트 설정 확인**
   - Framework Preset: Other
   - Build Command: (비워둠)
   - Output Directory: (비워둠)
   - Install Command: `pip install -r requirements.txt`

---

## 📚 참고 문서

- `docs/VERCEL_ENV_SETUP.md` - 환경변수 설정 완전 가이드
- `docs/08_Vercel_Architecture_Guide.md` - Vercel 아키텍처
- `CLAUDE.md` - Vercel Deployment Troubleshooting 섹션
- https://vercel.com/docs/errors/FUNCTION_INVOCATION_FAILED - 공식 문서

---

**작성일:** 2026-03-14
**업데이트:** 모든 코드 개선 적용 완료
