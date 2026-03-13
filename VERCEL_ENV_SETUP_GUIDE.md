# Vercel 환경변수 설정 가이드

**작성일:** 2026-03-13
**목적:** Vercel에 필수 환경변수 설정

---

## 🎯 설정할 환경변수 목록

### 필수 환경변수 (6개)

| 변수명 | 값 | 환경 |
|--------|-----|------|
| `SUPABASE_URL` | `https://yietqoikdaqpwmmvamtv.supabase.co` | 모든 환경 |
| `SUPABASE_KEY` | `eyJhbGciOiJI...` (anon key) | 모든 환경 |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJI...` (service role key) | 모든 환경 |
| `APP_ENV` | `production` / `preview` / `development` | 환경별 |
| `DEBUG` | `false` (production/preview), `true` (development) | 환경별 |
| `AI_PROVIDER` | `openai` | 모든 환경 |

### 선택 환경변수 (1개)

| 변수명 | 값 | 비고 |
|--------|-----|------|
| `OPENAI_API_KEY` | `sk-...` | Chat API 사용 시 필요 |

---

## ⭐ 방법 1: Vercel Dashboard (가장 쉬움, 권장)

### Step 1: Vercel Dashboard 접속

1. 브라우저에서 https://vercel.com/dashboard 접속
2. 로그인
3. 프로젝트 선택 (homesignal-ai 또는 배포된 프로젝트명)

### Step 2: 환경변수 페이지 이동

1. **Settings** 탭 클릭
2. 왼쪽 메뉴에서 **Environment Variables** 클릭

### Step 3: 환경변수 추가

아래 변수들을 하나씩 추가:

#### 1. SUPABASE_URL
- **Name:** `SUPABASE_URL`
- **Value:** `https://yietqoikdaqpwmmvamtv.supabase.co`
- **Environments:** ✅ Production, ✅ Preview, ✅ Development
- **Save** 클릭

#### 2. SUPABASE_KEY
- **Name:** `SUPABASE_KEY`
- **Value:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMjMyNjksImV4cCI6MjA4NzU5OTI2OX0.cnGFGUsn05TpVIvZyk6Sn6jEUdkTPzqc9YHOLnPr6NY
```
- **Environments:** ✅ Production, ✅ Preview, ✅ Development
- **Save** 클릭

#### 3. SUPABASE_SERVICE_ROLE_KEY
- **Name:** `SUPABASE_SERVICE_ROLE_KEY`
- **Value:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlpZXRxb2lrZGFxcHdtbXZhbXR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAyMzI2OSwiZXhwIjoyMDg3NTk5MjY5fQ.F4HvWwUiFMysGP06DW45v5RbxG7UoW38q8JI2z1MIDM
```
- **Environments:** ✅ Production, ✅ Preview, ✅ Development
- **Save** 클릭

#### 4. APP_ENV (환경별로 다르게)
**Production:**
- **Name:** `APP_ENV`
- **Value:** `production`
- **Environments:** ✅ Production
- **Save** 클릭

**Preview:**
- **Name:** `APP_ENV`
- **Value:** `preview`
- **Environments:** ✅ Preview
- **Save** 클릭

**Development:**
- **Name:** `APP_ENV`
- **Value:** `development`
- **Environments:** ✅ Development
- **Save** 클릭

#### 5. DEBUG (환경별로 다르게)
**Production & Preview:**
- **Name:** `DEBUG`
- **Value:** `false`
- **Environments:** ✅ Production, ✅ Preview
- **Save** 클릭

**Development:**
- **Name:** `DEBUG`
- **Value:** `true`
- **Environments:** ✅ Development
- **Save** 클릭

#### 6. AI_PROVIDER
- **Name:** `AI_PROVIDER`
- **Value:** `openai`
- **Environments:** ✅ Production, ✅ Preview, ✅ Development
- **Save** 클릭

#### 7. OPENAI_API_KEY (선택사항)
**OpenAI API 키가 있는 경우:**
- **Name:** `OPENAI_API_KEY`
- **Value:** `sk-proj-...` (실제 OpenAI API 키)
- **Environments:** ✅ Production, ✅ Preview, ✅ Development
- **Save** 클릭

**없는 경우:** 건너뛰기 (나중에 추가 가능)

### Step 4: 재배포 (중요!)

환경변수 추가 후 **반드시 재배포** 필요:

1. **Deployments** 탭으로 이동
2. 최신 배포의 **⋯** (점 3개) 메뉴 클릭
3. **Redeploy** 클릭
4. 확인

---

## 🚀 방법 2: Vercel CLI (자동화)

### Step 1: Vercel CLI 설치

```bash
# Node.js가 설치되어 있어야 함
npm i -g vercel
```

### Step 2: Vercel 로그인

```bash
vercel login
```

### Step 3: Python 스크립트 실행

```bash
# Python 스크립트로 자동 설정
python scripts/setup_vercel_env.py
```

스크립트가 자동으로:
- Supabase 환경변수 설정
- App 설정 환경변수 설정
- OPENAI_API_KEY 입력 요청 (선택사항)

### Step 4: 수동 확인

```bash
# 설정된 환경변수 확인
vercel env ls
```

---

## 📋 환경변수 설정 체크리스트

### 설정 완료 확인
- [ ] SUPABASE_URL 설정 완료
- [ ] SUPABASE_KEY 설정 완료
- [ ] SUPABASE_SERVICE_ROLE_KEY 설정 완료
- [ ] APP_ENV 설정 완료 (환경별)
- [ ] DEBUG 설정 완료 (환경별)
- [ ] AI_PROVIDER 설정 완료
- [ ] OPENAI_API_KEY 설정 완료 (선택)

### 재배포 확인
- [ ] Vercel Dashboard에서 Redeploy 실행
- [ ] 배포 완료 대기 (1-3분)
- [ ] 배포 상태 확인

---

## ✅ 배포 후 검증

### Health Check

```bash
curl https://your-backend.vercel.app/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "0.1.0"
}
```

### Root Endpoint

```bash
curl https://your-backend.vercel.app/
```

**예상 응답:**
```json
{
  "message": "HomeSignal AI API",
  "docs": "Disabled in production",
  "endpoints": {
    "forecast": "/api/v1/forecast",
    "chat": "/api/v1/chat",
    "news": "/api/v1/news/insights",
    ...
  }
}
```

### Mock API 테스트

```bash
# Forecast API (Mock 응답)
curl -X POST https://your-backend.vercel.app/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{"region": "청량리동", "period": "week", "horizon": 12}'
```

---

## 🔧 문제 해결

### 환경변수가 적용되지 않음

**해결:**
1. Vercel Dashboard에서 환경변수 재확인
2. **Redeploy** 버튼 클릭 (환경변수 변경 후 필수)
3. 배포 완료 대기

### "placeholder" URL 오류

**증상:**
```json
{
  "error": "Production 환경에서 placeholder Supabase URL을 사용할 수 없습니다"
}
```

**해결:**
- SUPABASE_URL 환경변수가 올바르게 설정되었는지 확인
- 재배포 실행

### OPENAI_API_KEY 없음

**증상:**
- Chat API가 작동하지 않음

**해결:**
- OpenAI API 키 발급: https://platform.openai.com/api-keys
- Vercel Dashboard에서 OPENAI_API_KEY 추가
- 재배포

---

## 💡 추가 정보

### 환경변수 우선순위

1. **Production:** 실제 서비스 환경
2. **Preview:** Pull Request 배포 (테스트)
3. **Development:** 로컬 개발 (`vercel dev`)

### 환경변수 삭제

Vercel Dashboard에서:
1. Settings → Environment Variables
2. 삭제할 변수의 **⋯** 메뉴 클릭
3. **Remove** 클릭

### 환경변수 수정

Vercel Dashboard에서:
1. 기존 변수 삭제
2. 새로운 값으로 다시 추가
3. **Redeploy** 실행

---

## 📚 관련 문서

- **Vercel 공식 문서:** https://vercel.com/docs/projects/environment-variables
- **VERCEL_DEPLOYMENT_GUIDE.md** - 전체 배포 가이드
- **VERCEL_DEPLOY_CHECKLIST.md** - 배포 체크리스트

---

## 🎯 요약

### 가장 빠른 방법 (5분)

1. ✅ https://vercel.com/dashboard 접속
2. ✅ Settings → Environment Variables
3. ✅ 위의 7개 변수 추가
4. ✅ Deployments → Redeploy
5. ✅ Health check 확인

**완료!** 🎉

---

**작성자:** Claude Code
**최종 업데이트:** 2026-03-13
