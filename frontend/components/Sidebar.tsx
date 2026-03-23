'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import {
  LayoutGrid,
  Map,
  TrendingUp,
  Search,
  FileText,
  MapPin,
  Home,
} from 'lucide-react'

const navItems = [
  { href: '/', label: '종합 개요', icon: LayoutGrid },
  { href: '/news', label: '지역 분석', icon: Map },
  { href: '/forecast', label: '가격 동향', icon: TrendingUp },
  { href: '/search', label: '아파트 검색', icon: Search },
  { href: '/chat', label: 'AI 리포트', icon: FileText },
]

const districts = [
  { label: '동대문구', href: '/forecast?gu=dongdaemun' },
  { label: '성북구', href: '/forecast?gu=seongbuk' },
  { label: '중랑구', href: '/forecast?gu=jungnang' },
  { label: '강북구', href: '/forecast?gu=gangbuk' },
  { label: '도봉구', href: '/forecast?gu=dobong' },
]

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname?.startsWith(href.split('?')[0])
  }

  return (
    <aside className="w-56 min-h-screen bg-background-surface border-r border-background-border flex flex-col shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-4 border-b border-background-border">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Image
            src="/logo-grid.svg"
            alt="홈시그널AI"
            width={28}
            height={28}
            priority
          />
          <span className="text-lg font-bold text-primary">홈시그널AI</span>
        </Link>
        <Link href="/" className="ml-auto text-gray-400 hover:text-gray-200 transition-colors">
          <Home className="w-4 h-4" />
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                ${active
                  ? 'bg-background-hover text-primary'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-background-hover'
                }
              `}
            >
              <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-primary' : ''}`} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Divider */}
      <div className="mx-4 border-t border-background-border" />

      {/* District Buttons */}
      <div className="px-3 py-4 space-y-2">
        {districts.map((district) => (
          <Link
            key={district.label}
            href={district.href}
            className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg border border-background-border text-sm text-gray-300 hover:border-primary hover:text-primary transition-colors"
          >
            <MapPin className="w-4 h-4 shrink-0" />
            {district.label}
          </Link>
        ))}
      </div>
    </aside>
  )
}
