'use client'

import React from 'react'
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts'

interface PredictionDataPoint {
  date: string
  predicted_price: number
  lower_bound?: number
  upper_bound?: number
  actual_price?: number
}

interface PredictionChartProps {
  data: PredictionDataPoint[]
  showConfidenceInterval?: boolean
  className?: string
}

export function PredictionChart({
  data,
  showConfidenceInterval = true,
  className = '',
}: PredictionChartProps) {
  const formatPrice = (value: number) => {
    return `${(value / 100000000).toFixed(1)}억`
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  return (
    <div className={`card-surface p-6 ${className}`}>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data}>
          <defs>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#374151"
            vertical={false}
          />
          
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            stroke="#6B7280"
            axisLine={{ stroke: '#374151' }}
          />
          
          <YAxis
            tickFormatter={formatPrice}
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            stroke="#6B7280"
            axisLine={{ stroke: '#374151' }}
            width={60}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '0.5rem',
              color: '#F9FAFB',
            }}
            labelStyle={{ color: '#D1D5DB', marginBottom: '8px' }}
            formatter={(value: number, name: string) => {
              const labels: Record<string, string> = {
                actual_price: '실거래가',
                predicted_price: '예측가',
                lower_bound: '하한',
                upper_bound: '상한',
              }
              return [formatPrice(value), labels[name] || name]
            }}
            labelFormatter={(label) => `날짜: ${label}`}
          />
          
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
            formatter={(value) => {
              const labels: Record<string, string> = {
                actual_price: '실거래가',
                predicted_price: '예측가',
                lower_bound: '신뢰구간 하한',
                upper_bound: '신뢰구간 상한',
              }
              return <span style={{ color: '#D1D5DB' }}>{labels[value] || value}</span>
            }}
          />
          
          {/* 신뢰구간 음영 */}
          {showConfidenceInterval && (
            <Area
              type="monotone"
              dataKey="upper_bound"
              stroke="none"
              fill="url(#confidenceGradient)"
              fillOpacity={1}
            />
          )}
          
          {/* 실거래가 (과거 데이터) */}
          <Line
            type="monotone"
            dataKey="actual_price"
            stroke="#FFFFFF"
            strokeWidth={1.5}
            dot={{ r: 3, fill: '#FFFFFF' }}
            activeDot={{ r: 5 }}
          />
          
          {/* 예측선 */}
          <Line
            type="monotone"
            dataKey="predicted_price"
            stroke="#3B82F6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 4, fill: '#3B82F6' }}
            activeDot={{ r: 6 }}
          />
          
          {/* 신뢰구간 경계선 */}
          {showConfidenceInterval && (
            <>
              <Line
                type="monotone"
                dataKey="lower_bound"
                stroke="#3B82F6"
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
                strokeOpacity={0.5}
              />
              <Line
                type="monotone"
                dataKey="upper_bound"
                stroke="#3B82F6"
                strokeWidth={1}
                strokeDasharray="2 2"
                dot={false}
                strokeOpacity={0.5}
              />
            </>
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
