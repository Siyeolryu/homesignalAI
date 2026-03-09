'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { TrendingUp, MessageSquare, Newspaper, Target, Shield, Percent } from 'lucide-react'
import { Disclaimer } from '@/components'

export default function Home() {
  const [selectedRegion, setSelectedRegion] = useState('')

  const regions = [
    '청량리',
    '회기',
    '휘경',
    '이문',
    '장안',
    '답십리',
    '전농',
    '용두',
  ]

  const features = [
    {
      icon: <Target className="w-8 h-8" />,
      title: '확률 기반 예측',
      description: '단순 추정이 아닌 신뢰구간과 확률을 제공합니다',
      color: 'text-accent',
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: '리스크 투명성',
      description: '변동성 등급과 시나리오 분석으로 불확실성을 명확히 전달합니다',
      color: 'text-primary',
    },
    {
      icon: <Percent className="w-8 h-8" />,
      title: '상승 확률 제공',
      description: '과거 패턴 기반 상승 가능성을 수치로 제시합니다',
      color: 'text-warning',
    },
  ]

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Image
              src="/logo-grid.svg"
              alt="HomeSignal AI Logo"
              width={64}
              height={64}
              priority
            />
          </div>
          <h1 className="text-5xl font-bold mb-4 text-balance">
            HomeSignal AI
          </h1>
          <p className="text-xl text-gray-400 text-balance max-w-2xl mx-auto">
            동대문구 부동산 시계열 예측 및 RAG 챗봇 서비스
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="card-surface p-8 hover-lift text-center"
            >
              <div className={`flex justify-center mb-4 ${feature.color}`}>
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Main Services */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <Link
            href="/forecast"
            className="card-surface p-8 hover-lift group"
          >
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-accent group-hover:text-accent-light transition-colors" />
              <h2 className="text-2xl font-semibold">가격 예측</h2>
            </div>
            <p className="text-gray-400 leading-relaxed">
              시계열 분석 기반 부동산 가격 예측 및 신뢰구간 제공
            </p>
          </Link>

          <Link
            href="/chat"
            className="card-surface p-8 hover-lift group"
          >
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-6 h-6 text-primary group-hover:text-primary-light transition-colors" />
              <h2 className="text-2xl font-semibold">AI 챗봇</h2>
            </div>
            <p className="text-gray-400 leading-relaxed">
              RAG 기반 부동산 정보 상담 및 맞춤형 분석
            </p>
          </Link>

          <Link
            href="/news"
            className="card-surface p-8 hover-lift group"
          >
            <div className="flex items-center gap-3 mb-4">
              <Newspaper className="w-6 h-6 text-warning group-hover:text-warning-light transition-colors" />
              <h2 className="text-2xl font-semibold">뉴스 분석</h2>
            </div>
            <p className="text-gray-400 leading-relaxed">
              키워드 기반 뉴스 인사이트 및 감성 시그널
            </p>
          </Link>
        </div>

        {/* Region Selection */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold mb-6 text-center">지역 선택</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {regions.map((region) => (
              <button
                key={region}
                onClick={() => setSelectedRegion(region)}
                className={`
                  p-5 rounded-lg font-semibold transition-all
                  ${
                    selectedRegion === region
                      ? 'bg-primary text-background-main border-2 border-primary shadow-lg'
                      : 'card-surface hover:bg-background-hover border-2 border-transparent'
                  }
                `}
              >
                {region}
              </button>
            ))}
          </div>
        </div>

        {selectedRegion && (
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-block card-surface px-8 py-4 rounded-full">
              <p className="text-lg">
                선택된 지역: <strong className="text-primary">{selectedRegion}</strong>
              </p>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <Disclaimer className="max-w-4xl mx-auto" />
      </div>
    </div>
  )
}
