# HomeSignal AI Frontend

동대문구 부동산 시계열 예측 및 RAG 챗봇 서비스의 Next.js 프론트엔드입니다.

## 디자인 시스템

### 컬러 시스템 (다크모드)

| 구분 | Hex Code | 사용 위치 |
|------|----------|-----------|
| Main BG | `#0B1220` | 전체 배경 (Deep Navy) |
| Surface | `#111827` | 카드 및 대시보드 모듈 |
| Primary | `#4ADE80` | 브랜드 컬러, 긍정/상승 |
| Accent | `#3B82F6` | AI 데이터, 예측선 |
| Danger | `#EF4444` | 경고, 부정 뉴스 |
| Warning | `#F59E0B` | 주의 |
| Negative | `#FB7185` | 부정 시그널 (Soft Red) |

### 컴포넌트

- **SummaryCard**: 요약 카드 (예측가, 신뢰구간 등)
- **PredictionChart**: 신뢰구간 포함 예측 차트
- **ScenarioCard**: 시나리오 카드 (비관/기본/낙관)
- **Badge**: 변동성 등급, 감성 시그널 뱃지
- **NewsCard**: 뉴스 카드 (감성 뱃지, 영향도)
- **Accordion**: 예측 근거 Accordion
- **Disclaimer**: 디스클레이머 컴포넌트
- **SearchBar**: 검색바
- **RegionSelector**: 지역 선택 드롭다운

### 페이지 구조

```
app/
├── page.tsx           # 홈 (3x3 로고, Feature 카드, 지역 선택)
├── forecast/page.tsx  # 예측 (신뢰구간, 시나리오, 근거)
├── chat/page.tsx      # 챗봇 (감성 시그널)
├── news/page.tsx      # 뉴스 (감성 뱃지, 히트맵 범례)
└── layout.tsx         # GNB (검색바, 지역 선택)
```

## 개발 명령어

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start

# 린트
npm run lint
```

## 환경 변수

`.env.local` 파일 생성:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## 디자인 원칙

### 1. 정보 우선순위
- 예측가가 가장 눈에 잘 보이는 위치
- 신뢰구간 반드시 함께 노출
- 상승 확률 명확히 % 표시
- 변동성 등급 시각적 구분

### 2. 리스크 투명성
- 숫자 하나가 아닌 "구간" 제공
- 신뢰구간 차트에서 명확히 구분
- 예측 하락 시 공포 색상(빨강) 과다 사용 금지
- 디스클레이머 상시 노출

### 3. 정책 준수

**금지 문구**:
- "매수 추천" ❌
- "확실한 상승" ❌
- "지금 사세요" ❌

**허용 표현**:
- "상승 확률" ✅
- "예측 범위" ✅
- "변동성 확대 구간" ✅

## 기술 스택

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS (다크모드)
- **Charts**: Recharts
- **Icons**: Lucide React
- **State**: React Query
- **Font**: Pretendard

## 브레이크포인트

- Desktop: 1440px
- Laptop: 1280px
- Tablet: 768px
- Mobile: 375px

## 배포

Vercel을 통해 배포됩니다. 자세한 내용은 `VERCEL_DEPLOYMENT_GUIDE.md`를 참조하세요.
