import React from 'react'

type BadgeVariant = 
  | 'grade-a' 
  | 'grade-b' 
  | 'grade-c' 
  | 'positive' 
  | 'negative' 
  | 'neutral'
  | 'stable'
  | 'moderate'
  | 'high'
  | 'critical'

interface BadgeProps {
  variant: BadgeVariant
  children: React.ReactNode
  className?: string
}

export function Badge({ variant, children, className = '' }: BadgeProps) {
  const getVariantStyles = () => {
    switch (variant) {
      // 변동성 등급
      case 'grade-a':
        return 'bg-primary/10 text-primary border-primary/20'
      case 'grade-b':
        return 'bg-warning/10 text-warning border-warning/20'
      case 'grade-c':
        return 'bg-danger/10 text-danger border-danger/20'
      
      // 감성 시그널
      case 'positive':
        return 'bg-primary/10 text-primary border-primary/20'
      case 'negative':
        return 'bg-negative/10 text-negative border-negative/20'
      case 'neutral':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
      
      // 공급 상태
      case 'stable':
        return 'bg-teal/10 text-teal border-teal/20'
      case 'moderate':
        return 'bg-warning/10 text-warning border-warning/20'
      case 'high':
        return 'bg-orange/10 text-orange border-orange/20'
      case 'critical':
        return 'bg-deepRed/10 text-deepRed border-deepRed/20'
      
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
  }

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium
        border ${getVariantStyles()} ${className}
      `}
    >
      {children}
    </span>
  )
}

interface VolatilityBadgeProps {
  grade: 'A' | 'B' | 'C'
  className?: string
}

export function VolatilityBadge({ grade, className = '' }: VolatilityBadgeProps) {
  const labels = {
    A: '낮음',
    B: '보통',
    C: '높음',
  }

  const variants: Record<string, BadgeVariant> = {
    A: 'grade-a',
    B: 'grade-b',
    C: 'grade-c',
  }

  return (
    <Badge variant={variants[grade]} className={className}>
      변동성 {grade} ({labels[grade]})
    </Badge>
  )
}
