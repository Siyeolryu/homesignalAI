# Vercel 환경변수 설정 가이드

## 배포 전 필수 작업

Vercel 배포 시 환경변수가 누락되면 `ValidationError: Field required` 오류가 발생합니다.
아래 단계를 따라 환경변수를 설정하세요.

---

## 1. Vercel CLI를 통한 환경변수 설정 (권장)

### 방법 A: 대화형 설정

```bash
# Production 환경변수 추가
vercel env add SUPABASE_URL production
vercel env add SUPABASE_KEY production
vercel env add SUPABASE_SERVICE_ROLE_KEY production
vercel env add OPENAI_API_KEY production

# Preview/Development 환경도 필요시 추가
vercel env add SUPABASE_URL preview
vercel env add SUPABASE_URL development
```

각 명령 실행 시 값을 입력하라는 프롬프트가 나타납니다.

### 방법 B: 스크립트를 통한 일괄 설정

```bash
# 환경변수 설정 스크립트 실행
uv run python scripts/setup_vercel_env.py
```

이 스크립트는 `.env` 파일을 읽어 Vercel에 자동으로 설정합니다.

---

## 2. Vercel Dashboard를 통한 설정

1. **Vercel Dashboard 접속**: https://vercel.com/dashboard
2. **프로젝트 선택**: HomeSignal AI 프로젝트 클릭
3. **Settings 탭** → **Environment Variables** 메뉴
4. 아래 환경변수 추가:

### 필수 환경변수 (Production)

| Key | Example Value | Description |
|-----|--------------|-------------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase 프로젝트 URL |
| `SUPABASE_KEY` | `eyJhbG...` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbG...` | Supabase service_role key (INSERT/UPDATE용) |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI API 키 (또는 ANTHROPIC_API_KEY) |

### 선택적 환경변수

| Key | Default | Description |
|-----|---------|-------------|
| `AI_PROVIDER` | `openai` | `openai` 또는 `anthropic` |
| `APP_ENV` | `development` | `production` 권장 |
| `DEBUG` | `true` | `false` 권장 (프로덕션) |
| `ALLOWED_ORIGINS` | `""` | CORS 허용 도메인 (쉼표 구분) |
| `SUPABASE_TIMEOUT` | `10` | Supabase 쿼리 타임아웃 (초) |
| `AI_API_TIMEOUT` | `30.0` | AI API 호출 타임아웃 (초) |
| `ENABLE_QUERY_PLANNER` | `true` | 쿼리 플래너 활성화 |

### 5. **Environment 선택**: Production, Preview, Development 중 선택
   - **Production**: 실제 사용자용
   - **Preview**: PR 미리보기용
   - **Development**: 로컬 개발용 (`vercel dev` 실행 시)

---

## 3. 환경변수 확인

### Vercel CLI로 확인

```bash
# Production 환경변수 목록 조회
vercel env ls production

# 특정 환경변수 값 확인 (마스킹됨)
vercel env pull .env.production
cat .env.production
```

### Dashboard에서 확인

Settings → Environment Variables에서 설정된 변수 목록 확인

---

## 4. 재배포 (환경변수 적용)

환경변수를 추가하거나 수정한 후 **반드시 재배포**해야 적용됩니다.

```bash
# 재배포 트리거
vercel --prod

# 또는 Git push (자동 배포 설정 시)
git push origin main
```

---

## 5. 문제 해결

### 오류: `ValidationError: Field required [type=missing]`

**원인**: 필수 환경변수(`SUPABASE_URL`, `SUPABASE_KEY`)가 Vercel에 설정되지 않음

**해결**:
```bash
# 1. 환경변수 설정 확인
vercel env ls production

# 2. 누락된 변수 추가
vercel env add SUPABASE_URL production
vercel env add SUPABASE_KEY production

# 3. 재배포
vercel --prod
```

### 오류: 환경변수는 있는데도 읽히지 않음

**원인**: Vercel의 환경변수 캐싱 또는 배포 시점 문제

**해결**:
```bash
# 1. 환경변수 삭제 후 재추가
vercel env rm SUPABASE_URL production
vercel env add SUPABASE_URL production

# 2. 강제 재배포
vercel --prod --force
```

### 환경변수 검증 스크립트 실행

```bash
# 로컬에서 환경변수 검증
uv run python scripts/validate_env.py

# Vercel 환경변수 검증 (배포 후)
curl https://your-app.vercel.app/health
```

---

## 6. 보안 권장사항

### ⚠️ 절대 하지 말 것

1. **환경변수를 코드에 하드코딩**
   ```python
   # ❌ 나쁜 예
   SUPABASE_URL = "https://xxx.supabase.co"
   ```

2. **프론트엔드 환경변수(`NEXT_PUBLIC_*`)에 API 키 저장**
   ```bash
   # ❌ 나쁜 예
   NEXT_PUBLIC_OPENAI_API_KEY=sk-...
   ```

3. **Git에 `.env` 파일 커밋**
   ```bash
   # .gitignore에 반드시 포함
   .env
   .env.local
   .env.production
   ```

### ✅ 권장사항

1. **민감한 키는 Service Role Key 사용**
   - `SUPABASE_SERVICE_ROLE_KEY`는 절대 클라이언트에 노출하지 않음
   - Ingest API 등 서버 전용 작업에만 사용

2. **프로덕션/개발 환경 분리**
   - 프로덕션: 실제 Supabase 프로젝트
   - 개발: 테스트용 Supabase 프로젝트 또는 Mock 모드

3. **CORS 도메인 제한**
   ```bash
   ALLOWED_ORIGINS=https://homesignal-ai.vercel.app
   ```

---

## 7. 자동화 스크립트

### `.env` → Vercel 환경변수 동기화 스크립트

`scripts/setup_vercel_env.py` 파일을 사용하여 로컬 `.env` 파일을 Vercel에 자동 업로드:

```bash
uv run python scripts/setup_vercel_env.py --environment production
```

스크립트는 다음을 수행합니다:
1. `.env` 파일 파싱
2. Vercel API를 통해 환경변수 추가
3. 설정 완료 확인

**주의**: Vercel CLI가 설치되어 있어야 합니다.

---

## 참고 문서

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [HomeSignal AI Architecture Guide](./08_Vercel_Architecture_Guide.md)
