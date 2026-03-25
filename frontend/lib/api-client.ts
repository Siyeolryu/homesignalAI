const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ---- Forecast ----

export interface ForecastParams {
  region: string
  period: 'week' | 'month'
  horizon: number
}

export interface PredictionPoint {
  date: string
  predicted_price: number
  lower_bound: number
  upper_bound: number
}

export interface ForecastData {
  predictions: PredictionPoint[]
  confidence_interval: boolean
  model_name: string
  model_version: string
  generated_at: string
  trend: string
}

export async function getForecast(params: ForecastParams): Promise<ForecastData> {
  const url = new URL(`${API_BASE_URL}/api/v1/forecast`)
  url.searchParams.set('region', params.region)
  url.searchParams.set('period', params.period)
  url.searchParams.set('horizon', String(params.horizon))

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`Forecast API error: ${res.status}`)

  const data = await res.json()

  return {
    predictions: (data.forecast ?? []).map((p: { date: string; value: number; lower_bound: number; upper_bound: number }) => ({
      date: p.date,
      predicted_price: p.value,
      lower_bound: p.lower_bound,
      upper_bound: p.upper_bound,
    })),
    confidence_interval: true,
    model_name: 'Prophet + LightGBM',
    model_version: data.model_version ?? 'v1.0',
    generated_at: new Date().toISOString(),
    trend: data.trend ?? '',
  }
}

// ---- Chat ----

export interface ChatSource {
  title: string
  url: string
}

export interface ChatData {
  response: string
  sources: ChatSource[]
}

export async function sendChatMessage(message: string, sessionId: string): Promise<ChatData> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`)

  const data = await res.json()

  return {
    response: data.answer ?? '',
    sources: (data.sources ?? []).map((s: { title: string; source: string }) => ({
      title: s.title,
      url: s.source,
    })),
  }
}

// ---- News ----

export interface KeywordFrequency {
  keyword: string
  frequency: number
  impact_score: number
}

export interface NewsItem {
  title: string
  content: string
  url: string
  published_at: string
  keywords: string[]
  impact_score: number
}

export interface NewsInsightsData {
  keyword_frequencies: KeywordFrequency[]
  recent_news: NewsItem[]
  summary: string
}

export async function getNewsInsights(keywords: string[], useRisePoints: boolean): Promise<NewsInsightsData> {
  const url = new URL(`${API_BASE_URL}/api/v1/news/insights`)
  keywords.forEach((kw) => url.searchParams.append('keywords', kw))
  if (useRisePoints) url.searchParams.set('use_rise_points', 'true')

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`News API error: ${res.status}`)

  const data = await res.json()

  return {
    keyword_frequencies: (data.insights ?? []).map((insight: { keyword: string; frequency: number; sentiment_score?: number }) => ({
      keyword: insight.keyword,
      frequency: insight.frequency,
      impact_score: insight.sentiment_score ?? 0,
    })),
    recent_news: [],
    summary: (data.top_issues ?? []).join(' | '),
  }
}
