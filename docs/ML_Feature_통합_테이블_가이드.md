# ML Feature 통합 테이블 가이드

**작성일**: 2026-03-09  
**목적**: Prophet + LightGBM 앙상블 모델 학습을 위한 통합 Feature 테이블 설계 및 사용법

---

## 1. 개요

HomeSignal AI의 시계열 예측 모델은 다음 데이터를 통합하여 학습합니다:

- **실거래가**: houses_data 테이블에서 주간/월간 집계
- **뉴스 키워드 빈도**: news_signals 테이블에서 카테고리별 집계
- **정책 이벤트**: policy_events 테이블에서 이벤트 더미 생성
- **계절성**: 날짜 기반 개학/이사/결혼 시즌 더미
- **이동평균**: 5주 단기, 20주 장기 MA

이 모든 피처를 **ml_training_features** 테이블에 통합하여 저장합니다.

---

## 2. 테이블 구조

### 2.1 ml_training_features

**목적**: 시계열 예측 모델 학습용 통합 Feature 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| period_date | DATE | 시계열 날짜 (주간: 월요일, 월간: 1일) |
| region | TEXT | 지역명 (예: 청량리동) |
| period_type | TEXT | 'week' 또는 'month' |
| avg_price | NUMERIC | 평균 실거래가 (Target 변수) |
| transaction_count | INT | 거래 건수 |
| ma_5_week | FLOAT | 5주 단기 이동평균 |
| ma_20_week | FLOAT | 20주 장기 이동평균 |
| news_gtx_freq | INT | GTX 관련 뉴스 빈도 |
| news_redevelopment_freq | INT | 재개발 관련 뉴스 빈도 |
| news_policy_freq | INT | 정책 관련 뉴스 빈도 |
| news_supply_freq | INT | 공급 관련 뉴스 빈도 |
| news_transport_freq | INT | 교통 관련 뉴스 빈도 |
| news_economic_freq | INT | 경제 지표 관련 뉴스 빈도 |
| news_social_freq | INT | 사회 이슈 관련 뉴스 빈도 |
| news_location_freq | INT | 지역 특정 뉴스 빈도 |
| event_gtx_announcement | BOOLEAN | GTX 개통/발표 더미 |
| event_redevelopment_approval | BOOLEAN | 재개발 승인 더미 |
| event_interest_rate_change | BOOLEAN | 금리 변동 더미 |
| event_loan_regulation | BOOLEAN | 대출 규제 변화 더미 |
| event_sales_restriction | BOOLEAN | 분양 규제 변화 더미 |
| season_school | BOOLEAN | 개학 시즌 (2-3월, 8-9월) |
| season_moving | BOOLEAN | 이사 시즌 (1-2월, 12월) |
| season_wedding | BOOLEAN | 결혼 시즌 (5월, 10월) |

### 2.2 policy_events

**목적**: 정책 이벤트 마스터 데이터

| 컬럼 | 타입 | 설명 |
|------|------|------|
| event_date | DATE | 이벤트 발생 날짜 |
| event_type | TEXT | 이벤트 타입 (gtx_announcement, interest_rate 등) |
| event_name | TEXT | 이벤트 명 |
| description | TEXT | 상세 설명 |
| impact_level | TEXT | 영향도 (low, medium, high) |
| region | TEXT | 영향 지역 (NULL이면 전체) |

---

## 3. Feature 생성 파이프라인

### 3.1 정책 이벤트 수집

```bash
# config/policy_events.yaml → policy_events 테이블
uv run python scripts/collect_policy_events.py

# Dry-run (미리보기)
uv run python scripts/collect_policy_events.py --dry-run
```

### 3.2 ML Feature 생성

```bash
# 전체 지역, 전체 기간 Feature 생성
uv run python scripts/generate_ml_features.py

# 특정 기간만 생성
uv run python scripts/generate_ml_features.py --start-date 2024-01-01 --end-date 2024-12-31

# 특정 지역만 생성
uv run python scripts/generate_ml_features.py --region 청량리동

# 월간 단위로 생성
uv run python scripts/generate_ml_features.py --period-type month

# Dry-run (실제 INSERT 없이 미리보기)
uv run python scripts/generate_ml_features.py --dry-run
```

**생성 프로세스:**
1. houses_data에서 주간/월간 집계 (avg_price, transaction_count)
2. news_signals에서 키워드 빈도 계산 (keywords.yaml 기반)
3. policy_events에서 이벤트 더미 생성
4. 날짜 기반 계절성 더미 계산
5. 이동평균 계산 (5주, 20주)
6. ml_training_features에 UPSERT

---

## 4. 모델 학습

### 4.1 학습 실행

```bash
# 청량리동, 주간 단위 모델 학습
uv run python scripts/train_forecast_model.py

# 특정 지역 학습
uv run python scripts/train_forecast_model.py --region 이문동

# 월간 단위 학습
uv run python scripts/train_forecast_model.py --period-type month

# Dry-run (평가만, 모델 저장 안 함)
uv run python scripts/train_forecast_model.py --dry-run
```

**학습 프로세스:**
1. ml_training_features에서 학습 데이터 로드
2. Train/Validation 분할 (80/20)
3. Prophet 학습 (트렌드, 계절성, Regressor)
4. LightGBM 학습 (모든 Feature)
5. 앙상블 평가 (RMSE, MAE, MAPE)
6. 모델 저장 (models/ 디렉토리)

### 4.2 학습 결과

학습 완료 후 다음 파일들이 생성됩니다:

```
models/
├── prophet_청량리동_week_v1.pkl
├── lightgbm_청량리동_week_v1.pkl
└── ensemble_청량리동_week_config.json
```

**ensemble_config.json 예시:**
```json
{
  "region": "청량리동",
  "period_type": "week",
  "prophet_weight": 0.6,
  "lightgbm_weight": 0.4,
  "metrics": {
    "prophet": {
      "rmse": 2.5,
      "mae": 1.8,
      "mape": 2.3
    },
    "lightgbm": {
      "rmse": 3.1,
      "mae": 2.2,
      "mape": 2.8
    },
    "ensemble": {
      "rmse": 2.2,
      "mae": 1.6,
      "mape": 2.0
    }
  },
  "trained_at": "2026-03-09"
}
```

---

## 5. 모델 서빙

### 5.1 ForecastService 통합

[src/forecast/service.py](src/forecast/service.py)가 자동으로 학습된 모델을 로드합니다:

```python
service = ForecastService(use_real_model=True)
forecast = await service.get_forecast(request)
```

**동작 방식:**
1. ModelLoader가 models/ 디렉토리에서 모델 로드
2. ml_training_features에서 최신 Feature 조회 (52주)
3. Prophet + LightGBM 예측 실행
4. 앙상블 가중 평균 (기본: Prophet 60%, LightGBM 40%)
5. 신뢰구간 포함 응답 반환

**Fallback:**
- 모델 파일이 없으면 자동으로 Mock 데이터 반환
- Feature 데이터가 없어도 Mock으로 대체

---

## 6. Feature 설명

### 6.1 Target 변수
- **avg_price**: 예측 대상 (주간/월간 평균 실거래가)

### 6.2 시계열 피처
- **ma_5_week**: 단기 추세 포착 (5주 이동평균)
- **ma_20_week**: 장기 추세 포착 (20주 이동평균)

### 6.3 뉴스 피처 (8개)
keywords.yaml의 카테고리별 뉴스 빈도:
- transport, redevelopment, policy, supply
- economic_indicators, social_issues, location_specific
- GTX는 별도 집계

### 6.4 이벤트 피처 (5개)
policy_events 테이블 기반 더미 변수:
- GTX 개통/발표
- 재개발 승인
- 금리 변동
- 대출 규제
- 분양 규제

### 6.5 계절성 피처 (3개)
날짜 기반 자동 생성:
- **개학 시즌**: 2-3월, 8-9월
- **이사 시즌**: 1-2월, 12월
- **결혼 시즌**: 5월, 10월

---

## 7. 데이터 요구사항

### 최소 데이터량
- **houses_data**: 최소 52주 (1년) 이상 (이동평균 계산)
- **news_signals**: 최소 100건 이상 (키워드 빈도 유의미성)
- **policy_events**: 최소 5개 이상 이벤트

### 데이터 수집 주기
- **실거래가**: 매주 월요일 (국토교통부 API)
- **뉴스**: 매일 (Google News 크롤러)
- **정책 이벤트**: 이벤트 발생 시 수동 입력

---

## 8. 모델 재학습 전략

### 재학습 주기
- **초기 (데이터 축적 단계)**: 매주 재학습
- **안정화 후**: 월 1회 재학습

### 재학습 트리거
- 새로운 실거래가 데이터 수집 후
- 주요 정책 이벤트 발생 후
- 모델 성능 저하 감지 시 (RMSE > 5%)

### 재학습 명령어
```bash
# 1. Feature 재생성
uv run python scripts/generate_ml_features.py

# 2. 모델 재학습
uv run python scripts/train_forecast_model.py

# 3. API 서버 재시작 (모델 리로드)
uv run uvicorn src.main:app --reload
```

---

## 9. 성능 최적화

### Feature 생성
- 배치 작업으로 실행 (매주 월요일 새벽)
- Incremental 업데이트 (신규 기간만 생성)

### 모델 예측
- 모델 로드는 @lru_cache로 캐싱
- Feature 조회는 최근 52주만
- 예측 결과는 Redis 캐싱 (1시간)

---

## 10. 트러블슈팅

### Q1. Feature 생성 시 데이터가 없다고 나옵니다.
**A**: houses_data와 news_signals에 데이터가 있는지 확인하세요.
```sql
SELECT COUNT(*) FROM houses_data;
SELECT COUNT(*) FROM news_signals;
```

### Q2. 모델 학습 시 Feature가 부족하다고 나옵니다.
**A**: 최소 52주 이상의 Feature가 필요합니다. generate_ml_features.py를 먼저 실행하세요.

### Q3. API 응답이 여전히 Mock 데이터입니다.
**A**: 
1. models/ 디렉토리에 모델 파일이 있는지 확인
2. ForecastService(use_real_model=True)로 초기화되었는지 확인
3. 모델 파일명이 `prophet_{region}_{period_type}_v1.pkl` 형식인지 확인

### Q4. 특정 지역의 모델만 학습하고 싶습니다.
**A**: 
```bash
uv run python scripts/train_forecast_model.py --region 청량리동
```

---

## 11. 다음 단계

### 즉시 실행 가능
1. Supabase SQL Editor에서 `migrations/004_create_ml_features_tables.sql` 실행
2. 정책 이벤트 수집: `uv run python scripts/collect_policy_events.py`
3. Feature 생성: `uv run python scripts/generate_ml_features.py --dry-run` (미리보기)

### 데이터 수집 후 실행
4. 실거래가 데이터 수집 (houses_data에 최소 52주)
5. 뉴스 데이터 수집 (news_signals에 최소 100건)
6. Feature 생성: `uv run python scripts/generate_ml_features.py`
7. 모델 학습: `uv run python scripts/train_forecast_model.py`

### 프로덕션 배포
8. API 서버 재시작 (모델 로드)
9. 예측 API 테스트
10. 성능 모니터링

---

## 12. 참고 문서

- [docs/03_AI_Model_Pipeline.md](03_AI_Model_Pipeline.md): ML 파이프라인 상세
- [migrations/004_create_ml_features_tables.sql](../migrations/004_create_ml_features_tables.sql): 테이블 스키마
- [config/policy_events.yaml](../config/policy_events.yaml): 정책 이벤트 정의
- [config/keywords.yaml](../config/keywords.yaml): 뉴스 키워드 정의

---

**구현 완료**: 2026-03-09
