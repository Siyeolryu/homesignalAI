'use client'

import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { SearchBar, RegionSelector } from '@/components'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  const navItems = [
    { href: '/', label: '홈' },
    { href: '/forecast', label: '가격 예측' },
    { href: '/chat', label: 'AI 챗봇' },
    { href: '/news', label: '뉴스 분석' },
  ]

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname?.startsWith(href)
  }

  return (
    <html lang="ko" className="dark">
      <head>
        <title>HomeSignal AI - 동대문구 부동산 예측</title>
        <meta name="description" content="동대문구 부동산 시계열 예측 및 RAG 챗봇 서비스" />
      </head>
      <body className="font-sans antialiased">
        <Providers>
          {/* Global Navigation Bar */}
          <nav className="bg-background-surface border-b border-background-border sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                  <Image
                    src="/logo-grid.svg"
                    alt="HomeSignal AI"
                    width={32}
                    height={32}
                    priority
                  />
                  <span className="text-xl font-bold text-primary">
                    HomeSignal AI
                  </span>
                </Link>

                {/* Navigation Links */}
                <div className="hidden md:flex items-center gap-1">
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`
                        px-4 py-2 rounded-lg text-sm font-medium transition-colors
                        ${
                          isActive(item.href)
                            ? 'bg-primary text-background-main'
                            : 'text-gray-400 hover:text-gray-200 hover:bg-background-hover'
                        }
                      `}
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>

                {/* Right Section: Search + Region */}
                <div className="flex items-center gap-3">
                  <SearchBar
                    placeholder="지역, 키워드 검색..."
                    className="hidden lg:block w-64"
                  />
                  <RegionSelector />
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-background-surface border-t border-background-border mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <Image
                    src="/logo-grid.svg"
                    alt="HomeSignal AI"
                    width={24}
                    height={24}
                  />
                  <p className="text-sm text-gray-400">
                    © 2026 HomeSignal AI. All rights reserved.
                  </p>
                </div>
                <p className="text-xs text-gray-500 text-center">
                  본 서비스는 투자 권유가 아니며 정보 제공 목적입니다.
                </p>
              </div>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  )
}
