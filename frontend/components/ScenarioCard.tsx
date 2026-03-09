import React from 'react'
import { TrendingDown, TrendingUp, Minus } from 'lucide-react'

type ScenarioType = 'pessimistic' | 'base' | 'optimistic'

interface ScenarioCardProps {
  type: ScenarioType
  price: number
  probability: number
  description: string
  className?: string
}

export function ScenarioCard({
  type,
  price,
  probability,
  description,
  className = '',
}: ScenarioCardProps) {
  const getScenarioConfig = () => {
    switch (type) {
      case 'pessimistic':
        return {
          label: '비관 시나리오',
          icon: <TrendingDown className="w-6 h-6" />,
          color: 'text-danger',
          bgColor: 'bg-danger/10',
          borderColor: 'border-danger/20',
        }
      case 'optimistic':
        return {
          label: '낙관 시나리오',
          icon: <TrendingUp className="w-6 h-6" />,
          color: 'text-primary',
          bgColor: 'bg-primary/10',
          borderColor: 'border-primary/20',
        }
      default:
        return {
          label: '기본 시나리오',
          icon: <Minus className="w-6 h-6" />,
          color: 'text-accent',
          bgColor: 'bg-accent/10',
          borderColor: 'border-accent/20',
        }
    }
  }

  const config = getScenarioConfig()
  const formattedPrice = (price / 100000000).toFixed(2)

  return (
    <div
      className={`
        card-surface p-6 border-2 ${config.borderColor} hover-lift
        ${className}
      `}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={`${config.color}`}>{config.icon}</div>
        <h3 className="text-lg font-semibold">{config.label}</h3>
      </div>
      
      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-400 mb-1">예측 가격</p>
          <p className={`text-3xl font-bold ${config.color} price-format`}>
            {formattedPrice}억 원
          </p>
        </div>
        
        <div>
          <p className="text-sm text-gray-400 mb-1">발생 확률</p>
          <p className="text-xl font-semibold text-gray-200">
            {probability.toFixed(1)}%
          </p>
        </div>
        
        <div className={`${config.bgColor} rounded-lg p-3 mt-4`}>
          <p className="text-sm text-gray-300 leading-relaxed">
            {description}
          </p>
        </div>
      </div>
    </div>
  )
}
