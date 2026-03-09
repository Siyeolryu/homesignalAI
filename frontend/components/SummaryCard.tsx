import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface SummaryCardProps {
  label: string
  value: string | number
  change?: number
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ReactNode
  unit?: string
  className?: string
}

export function SummaryCard({
  label,
  value,
  change,
  trend,
  icon,
  unit,
  className = '',
}: SummaryCardProps) {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-primary'
    if (trend === 'down') return 'text-negative'
    return 'text-gray-400'
  }

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4" />
    return <Minus className="w-4 h-4" />
  }

  return (
    <div
      className={`card-surface p-6 hover-lift ${className}`}
    >
      <div className="flex items-start justify-between mb-3">
        <p className="text-sm text-gray-400">{label}</p>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold price-format">
            {value}
            {unit && <span className="text-lg text-gray-400 ml-1">{unit}</span>}
          </p>
        </div>
        
        {change !== undefined && (
          <div className={`flex items-center gap-1 ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="text-sm font-semibold">
              {change > 0 ? '+' : ''}
              {change.toFixed(2)}%
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
