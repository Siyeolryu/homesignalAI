'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Newspaper, TrendingUp, Calendar, Filter } from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { getNewsInsights } from '@/lib/api-client'
import { NewsCard, Badge } from '@/components'

export default function NewsPage() {
  const [keywords, setKeywords] = useState(['GTX', '재개발', '청량리'])
  const [useRisePoints, setUseRisePoints] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['news-insights', keywords, useRisePoints],
    queryFn: () => getNewsInsights(keywords, useRisePoints),
  })

  const availableKeywords = [
    'GTX',
    'GTX-C',
    '청량리역',
    '재개발',
    '뉴타운',
    '이문휘경뉴타운',
    '분양',
    '입주',
    '금리',
    '대출',
  ]

  const toggleKeyword = (keyword: string) => {
    setKeywords((prev) =>
      prev.includes(keyword)
        ? prev.filter((k) => k !== keyword)
        : [...prev, keyword]
    )
  }

  const mockSentiment = (title: string): 'positive' | 'negative' | 'neutral' => {
    if (title.includes('상승') || title.includes('호재') || title.includes('개통')) return 'positive'
    if (title.includes('하락') || title.includes('악재') || title.includes('규제')) return 'negative'
    return 'neutral'
  }

  const supplyLegend = [
    { label: '적정', color: '#14B8A6', range: '< 100%' },
    { label: '보통', color: '#F59E0B', range: '100-120%' },
    { label: '과다', color: '#EA580C', range: '120-150%' },
    { label: '과잉 경고', color: '#991B1B', range: '> 150%' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <Newspaper className="w-8 h-8 mr-3 text-warning" />
          뉴스 이슈 분석
        </h1>
      </div>

      {/* Controls */}
      <div className="card-surface p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-3 flex items-center">
              <Filter className="w-4 h-4 mr-1" />
              분석 키워드 선택
            </label>
            <div className="flex flex-wrap gap-2">
              {availableKeywords.map((keyword) => (
                <button
                  key={keyword}
                  onClick={() => toggleKeyword(keyword)}
                  className={`px-4 py-2 rounded-lg border-2 transition-colors font-medium ${
                    keywords.includes(keyword)
                      ? 'bg-primary text-background-main border-primary'
                      : 'bg-background-main text-gray-300 border-background-border hover:border-primary'
                  }`}
                >
                  {keyword}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useRisePoints"
              checked={useRisePoints}
              onChange={(e) => setUseRisePoints(e.target.checked)}
              className="w-4 h-4 accent-primary rounded"
            />
            <label
              htmlFor="useRisePoints"
              className="text-sm font-medium text-gray-400 flex items-center cursor-pointer"
            >
              <TrendingUp className="w-4 h-4 mr-1" />
              상승 시점 전후 뉴스만 분석
            </label>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center h-64 card-surface rounded-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-warning"></div>
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
        <div className="space-y-6">
          {/* Keyword Frequency Chart */}
          <div className="card-surface p-6">
            <h2 className="text-xl font-semibold mb-4">키워드 빈도 분석</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.keyword_frequencies}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="keyword"
                  tick={{ fill: '#9CA3AF', fontSize: 12 }}
                  stroke="#6B7280"
                />
                <YAxis
                  tick={{ fill: '#9CA3AF', fontSize: 12 }}
                  stroke="#6B7280"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem',
                    color: '#F9FAFB',
                  }}
                />
                <Legend
                  wrapperStyle={{ paddingTop: '20px' }}
                  formatter={(value) => (
                    <span style={{ color: '#D1D5DB' }}>{value}</span>
                  )}
                />
                <Bar dataKey="frequency" fill="#3B82F6" name="빈도" />
                <Bar dataKey="impact_score" fill="#F59E0B" name="영향도" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Supply Heatmap Legend */}
          <div className="card-surface p-6">
            <h3 className="text-lg font-semibold mb-4">공급 히트맵 범례</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {supplyLegend.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-4 bg-background-main rounded-lg"
                >
                  <div
                    className="w-6 h-6 rounded"
                    style={{ backgroundColor: item.color }}
                  />
                  <div>
                    <p className="text-sm font-semibold text-gray-200">
                      {item.label}
                    </p>
                    <p className="text-xs text-gray-500">{item.range}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Keywords Summary */}
          <div>
            <h3 className="text-lg font-semibold mb-3">주요 키워드</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {data.keyword_frequencies.slice(0, 4).map((item: any) => (
                <div key={item.keyword} className="card-surface p-5">
                  <p className="text-sm text-gray-400 mb-1">{item.keyword}</p>
                  <p className="text-3xl font-bold text-accent">{item.frequency}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    영향도: <span className="text-warning font-semibold">{item.impact_score?.toFixed(2) || 'N/A'}</span>
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Recent News with Sentiment */}
          {data.recent_news && data.recent_news.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                최근 뉴스
              </h3>
              <div className="grid gap-4">
                {data.recent_news.slice(0, 5).map((news: any, index: number) => (
                  <NewsCard
                    key={index}
                    title={news.title}
                    content={news.content}
                    url={news.url}
                    publishedAt={news.published_at}
                    keywords={news.keywords}
                    sentiment={mockSentiment(news.title)}
                    impactScore={news.impact_score}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          <div className="bg-accent/10 border border-accent/20 rounded-lg p-5">
            <h3 className="font-semibold mb-2 text-accent">분석 요약</h3>
            <p className="text-sm text-gray-300 leading-relaxed">
              {data.summary ||
                '선택한 키워드에 대한 뉴스 빈도와 영향도를 분석했습니다. 상승 시점 전후 분석을 활성화하면 가격 변동과 연관된 이슈를 더 정확히 파악할 수 있습니다.'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
