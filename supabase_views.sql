-- ================================================================
-- HomeSignal AI — Supabase SQL 뷰 생성
-- Supabase > SQL Editor 에서 순서대로 실행
-- ================================================================


-- ────────────────────────────────────────
-- View 1: 동별 월간 매매 집계
-- ────────────────────────────────────────
CREATE OR REPLACE VIEW v_monthly_trade AS
SELECT
    deal_year,
    deal_month,
    dong,
    COUNT(*)                                                          AS trade_count,
    ROUND(AVG(price_10k)::NUMERIC, 0)                                AS avg_price_10k,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP
          (ORDER BY price_10k)::NUMERIC, 0)                          AS median_price_10k,
    ROUND((AVG(price_10k) / NULLIF(AVG(area), 0))::NUMERIC, 1)      AS avg_price_per_sqm,
    ROUND(AVG(area)::NUMERIC, 2)                                     AS avg_area
FROM apt_trade
WHERE deal_year > 0
  AND price_10k > 0
GROUP BY deal_year, deal_month, dong;


-- ────────────────────────────────────────
-- View 2: 동별 월간 전세 집계
-- ────────────────────────────────────────
CREATE OR REPLACE VIEW v_monthly_jeonse AS
SELECT
    deal_year,
    deal_month,
    dong,
    COUNT(*)                                                          AS jeonse_count,
    ROUND(AVG(deposit_10k)::NUMERIC, 0)                              AS avg_deposit_10k,
    ROUND((AVG(deposit_10k) / NULLIF(AVG(area), 0))::NUMERIC, 1)    AS avg_deposit_per_sqm
FROM apt_rent
WHERE contract_type = '전세'
  AND deposit_10k > 0
  AND deal_year > 0
GROUP BY deal_year, deal_month, dong;


-- ────────────────────────────────────────
-- View 3: 동별 월간 월세 집계
-- ────────────────────────────────────────
CREATE OR REPLACE VIEW v_monthly_wolse AS
SELECT
    deal_year,
    deal_month,
    dong,
    COUNT(*)                                                          AS wolse_count,
    ROUND(AVG(monthly_rent_10k)::NUMERIC, 1)                         AS avg_monthly_rent_10k,
    ROUND(AVG(deposit_10k)::NUMERIC, 0)                              AS avg_wolse_deposit_10k
FROM apt_rent
WHERE contract_type = '월세'
  AND monthly_rent_10k > 0
  AND deal_year > 0
GROUP BY deal_year, deal_month, dong;


-- ────────────────────────────────────────
-- View 4: 모델 피처 통합 뷰
--   매매 + 전세 + 월세 + 금리 3종 JOIN
-- ────────────────────────────────────────
CREATE OR REPLACE VIEW v_model_features AS
SELECT
    t.deal_year,
    t.deal_month,
    t.dong,
    -- 매매
    t.trade_count,
    t.avg_price_10k,
    t.median_price_10k,
    t.avg_price_per_sqm,
    t.avg_area,
    -- 전세
    j.jeonse_count,
    j.avg_deposit_10k       AS avg_jeonse_10k,
    j.avg_deposit_per_sqm   AS avg_jeonse_per_sqm,
    -- 월세
    w.wolse_count,
    w.avg_monthly_rent_10k,
    -- 금리 3종
    ir_base.rate            AS rate_base,
    ir_cd.rate              AS rate_cd,
    ir_bond.rate            AS rate_bond3y
FROM v_monthly_trade t
LEFT JOIN v_monthly_jeonse j
       ON t.deal_year  = j.deal_year
      AND t.deal_month = j.deal_month
      AND t.dong       = j.dong
LEFT JOIN v_monthly_wolse w
       ON t.deal_year  = w.deal_year
      AND t.deal_month = w.deal_month
      AND t.dong       = w.dong
LEFT JOIN interest_rate ir_base
       ON EXTRACT(YEAR  FROM ir_base.stat_date)::INT = t.deal_year
      AND EXTRACT(MONTH FROM ir_base.stat_date)::INT = t.deal_month
      AND ir_base.rate_type = '기준금리'
LEFT JOIN interest_rate ir_cd
       ON EXTRACT(YEAR  FROM ir_cd.stat_date)::INT   = t.deal_year
      AND EXTRACT(MONTH FROM ir_cd.stat_date)::INT   = t.deal_month
      AND ir_cd.rate_type   = 'CD금리(91일)'
LEFT JOIN interest_rate ir_bond
       ON EXTRACT(YEAR  FROM ir_bond.stat_date)::INT = t.deal_year
      AND EXTRACT(MONTH FROM ir_bond.stat_date)::INT = t.deal_month
      AND ir_bond.rate_type = '국고채(3년)'
ORDER BY t.deal_year, t.deal_month, t.dong;


-- ────────────────────────────────────────
-- 검증 쿼리 (뷰 생성 후 확인)
-- ────────────────────────────────────────

-- 전체 행수 및 기간 확인
SELECT
    COUNT(*)                          AS total_rows,
    MIN(deal_year || '-' || LPAD(deal_month::TEXT, 2, '0')) AS min_ym,
    MAX(deal_year || '-' || LPAD(deal_month::TEXT, 2, '0')) AS max_ym,
    COUNT(DISTINCT dong)              AS dong_count
FROM v_model_features;

-- 동별 최근 3개월 매매가 및 전세가
SELECT
    dong,
    deal_year,
    deal_month,
    avg_price_10k,
    avg_jeonse_10k,
    ROUND((avg_jeonse_10k / NULLIF(avg_price_10k, 0) * 100)::NUMERIC, 1) AS jeonse_ratio_pct,
    rate_base
FROM v_model_features
WHERE deal_year = 2025 AND deal_month >= 10
ORDER BY dong, deal_year, deal_month;
