import React from 'react'
import { AlertCircle } from 'lucide-react'

interface DisclaimerProps {
  className?: string
}

export function Disclaimer({ className = '' }: DisclaimerProps) {
  return (
    <div
      className={`
        bg-background-hover border border-background-border rounded-lg p-4
        ${className}
      `}
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-sm text-gray-400 leading-relaxed">
            본 서비스는 투자 권유가 아니며 정보 제공 목적입니다.
          </p>
          <p className="text-xs text-gray-500 leading-relaxed">
            예측 결과는 과거 데이터 기반 통계 모델이며, 실제 시장 상황과 다를 수 있습니다.
            투자 결정 시 반드시 전문가와 상담하시기 바랍니다.
          </p>
        </div>
      </div>
    </div>
  )
}
