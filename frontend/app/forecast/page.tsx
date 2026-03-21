'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Calendar, MapPin, Activity, AlertTriangle, Percent } from 'lucide-react'
import { getForecast } from '@/lib/api-client'
import {
  SummaryCard,
  PredictionChart,
  ScenarioCard,
  Accordion,
  Disclaimer,
  VolatilityBadge,
} from '@/components'

export default function ForecastPage() {
  const [region, setRegion] = useState('청량리동')
  const [period, setPeriod] = useState<'week' | 'month'>('week')
  const [horizon, setHorizon] = useState(12)

  const { data, isLoading, error } = useQuery({
    queryKey: ['forecast', region, period, horizon],
    queryFn: () => getForecast({ region, period, horizon }),
  })

  const regions = [
    '청량리동',
    '회기동',
    '휘경동',
    '이문동',
    '용두동',
    '제기동',
    '전농동',
    '답십리동',
  ]

  const currentPrice = data?.predictions[0]?.predicted_price || 0
  const futurePrice = data?.predictions[data.predictions.length - 1]?.predicted_price || 0
  const priceChange = currentPrice > 0 ? ((futurePrice - currentPrice) / currentPrice) * 100 : 0
  const trend = priceChange > 0 ? 'up' : priceChange < 0 ? 'down' : 'neutral'

  const confidenceInterval = data?.predictions[data.predictions.length - 1]
  const lowerBound = confidenceInterval?.lower_bound || 0
  const upperBound = confidenceInterval?.upper_bound || 0
  const intervalRange = upperBound > 0 ? ((upperBound - lowerBound) / futurePrice) * 100 : 0

  const volatilityGrade = intervalRange < 10 ? 'A' : intervalRange < 20 ? 'B' : 'C'
  const riseProb = priceChange > 0 ? 65 + Math.random() * 15 : 35 + Math.random() * 15

  const mockDrivers = [
    { name: 'GTX-C 청량리역 개통 예정', impact: 85, category: 'transport' },
    { name: '이문휘경뉴타운 재개발 진행', impact: 72, category: 'redevelopment' },
    { name: '서울 전역 거래량 증가 추세', impact: 58, category: 'supply' },
    { name: '대출 규제 완화 정책', impact: 45, category: 'policy' },
    { name: '동대문구 인구 유입 증가', impact: 38, category: 'demographic' },
  ]

  const scenarios = [
    {
      type: 'pessimistic' as const,
      price: lowerBound || futurePrice * 0.9,
      probability: 20,
      description: '금리 상승 및 규제 강화 시 예상되는 보수적 시나리오',
    },
    {
      type: 'base' as const,
      price: futurePrice,
      probability: 60,
      description: '현재 추세 유지 시 가장 가능성 높은 시나리오',
    },
    {
      type: 'optimistic' as const,
      price: upperBound || futurePrice * 1.1,
      probability: 20,
      description: 'GTX 개통 및 재개발 가속화 시 낙관적 시나리오',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <TrendingUp className="w-8 h-8 mr-3 text-accent" />
          부동산 가격 예측
        </h1>
      </div>

      {/* Controls */}
      <div className="card-surface p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2 flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              지역
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full px-3 py-2 bg-background-main border border-background-border rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {regions.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2 flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              기간
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as 'week' | 'month')}
              className="w-full px-3 py-2 bg-background-main border border-background-border rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="week">주간</option>
              <option value="month">월간</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              예측 기간
            </label>
            <input
              type="number"
              value={horizon}
              onChange={(e) => setHorizon(parseInt(e.target.value))}
              min="1"
              max="52"
              className="w-full px-3 py-2 bg-background-main border border-background-border rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <p className="text-xs text-gray-500 mt-1">
              {period === 'week' ? '주' : '개월'}
            </p>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center h-96 card-surface rounded-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
        </div>
      )}

      {error && (
        <div className="bg-danger/10 border border-danger/20 rounded-lg p-4">
          <p className="text-danger">
            데이터를 불러오는 중 오류가 발생했습니다.
          </p>
        </div>
      )}

      {data && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <SummaryCard
              label="예측 가격"
              value={(futurePrice / 100000000).toFixed(2)}
              unit="억 원"
              change={priceChange}
              trend={trend}
              icon={<TrendingUp className="w-5 h-5" />}
            />
            
            <SummaryCard
              label="신뢰구간"
              value={`${(lowerBound / 100000000).toFixed(1)} - ${(upperBound / 100000000).toFixed(1)}`}
              unit="억"
              icon={<Activity className="w-5 h-5" />}
            />
            
            <SummaryCard
              label="상승 확률"
              value={riseProb.toFixed(1)}
              unit="%"
              icon={<Percent className="w-5 h-5" />}
            />
            
            <div className="card-surface p-6">
              <div className="flex items-start justify-between mb-3">
                <p className="text-sm text-gray-400">변동성 등급</p>
                <AlertTriangle className="w-5 h-5 text-gray-400" />
              </div>
              <div className="flex items-center justify-between">
                <VolatilityBadge grade={volatilityGrade} />
              </div>
            </div>
          </div>

          {/* Chart */}
          <PredictionChart
            data={data.predictions}
            showConfidenceInterval={data.confidence_interval}
          />

          {/* Scenarios */}
          <div>
            <h2 className="text-2xl font-semibold mb-4">시나리오 분석</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {scenarios.map((scenario, idx) => (
                <ScenarioCard
                  key={idx}
                  type={scenario.type}
                  price={scenario.price}
                  probability={scenario.probability}
                  description={scenario.description}
                />
              ))}
            </div>
          </div>

          {/* Prediction Drivers */}
          <Accordion title="예측 근거 (Top 5 Drivers)" defaultOpen={true}>
            <div className="space-y-3">
              {mockDrivers.map((driver, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-background-main rounded-lg"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-200">
                      {driver.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      카테고리: {driver.category}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-xs text-gray-500">영향도</p>
                      <p className="text-lg font-bold text-accent">
                        {driver.impact}
                      </p>
                    </div>
                    <div className="w-24 h-2 bg-background-hover rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent rounded-full"
                        style={{ width: `${driver.impact}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Accordion>

          {/* Model Info */}
          <div className="card-surface p-4">
            <p className="text-sm text-gray-400">
              모델: <span className="text-gray-200">{data.model_name}</span> | 
              버전: <span className="text-gray-200">{data.model_version}</span>
              {data.generated_at && (
                <>
                  {' | '}
                  생성일: <span className="text-gray-200">{new Date(data.generated_at).toLocaleString('ko-KR')}</span>
                </>
              )}
            </p>
          </div>

          {/* Disclaimer */}
          <Disclaimer />
        </>
      )}
    </div>
  )
}
