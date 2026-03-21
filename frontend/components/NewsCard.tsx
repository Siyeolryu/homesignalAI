import React from 'react'
import { Calendar, TrendingUp, TrendingDown } from 'lucide-react'
import { Badge } from './Badge'

interface NewsCardProps {
  title: string
  content?: string
  url?: string
  publishedAt?: string
  keywords?: string[]
  sentiment?: 'positive' | 'negative' | 'neutral'
  impactScore?: number
  className?: string
}

export function NewsCard({
  title,
  content,
  url,
  publishedAt,
  keywords = [],
  sentiment,
  impactScore,
  className = '',
}: NewsCardProps) {
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 24) return `${diffHours}시간 전`
    if (diffDays < 7) return `${diffDays}일 전`
    return date.toLocaleDateString('ko-KR')
  }

  return (
    <div
      className={`
        card-surface p-5 hover-lift cursor-pointer
        ${className}
      `}
      onClick={() => url && window.open(url, '_blank')}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h4 className="text-base font-semibold text-gray-100 leading-snug flex-1">
          {title}
        </h4>
        
        {sentiment && (
          <div className="flex items-center gap-1">
            {sentiment === 'positive' && (
              <>
                <TrendingUp className="w-4 h-4 text-primary" />
                <Badge variant="positive">긍정</Badge>
              </>
            )}
            {sentiment === 'negative' && (
              <>
                <TrendingDown className="w-4 h-4 text-negative" />
                <Badge variant="negative">부정</Badge>
              </>
            )}
            {sentiment === 'neutral' && (
              <Badge variant="neutral">중립</Badge>
            )}
          </div>
        )}
      </div>
      
      {content && (
        <p className="text-sm text-gray-400 mb-3 line-clamp-2 leading-relaxed">
          {content}
        </p>
      )}
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formatDate(publishedAt)}</span>
        </div>
        
        {impactScore !== undefined && (
          <div className="text-xs">
            <span className="text-gray-500">영향도: </span>
            <span className="text-accent font-semibold">
              {impactScore.toFixed(1)}
            </span>
          </div>
        )}
      </div>
      
      {keywords.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {keywords.slice(0, 5).map((keyword, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 bg-background-hover text-gray-400 text-xs rounded"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
