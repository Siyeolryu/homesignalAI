'use client'

import './globals.css'
import { Providers } from './providers'
import Image from 'next/image'
import { Sidebar } from '@/components'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="dark">
      <head>
        <title>홈시그널AI - 부동산 예측</title>
        <meta name="description" content="동대문구 부동산 시계열 예측 및 RAG 챗봇 서비스" />
      </head>
      <body className="font-sans antialiased">
        <Providers>
          <div className="flex min-h-screen">
            {/* Sidebar */}
            <Sidebar />

            {/* Main Area */}
            <div className="flex-1 flex flex-col min-w-0">
              {/* Main Content */}
              <main className="flex-1 px-6 py-8">
                {children}
              </main>

              {/* Footer */}
              <footer className="bg-background-surface border-t border-background-border">
                <div className="px-6 py-6">
                  <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <Image
                        src="/logo-grid.svg"
                        alt="홈시그널AI"
                        width={20}
                        height={20}
                      />
                      <p className="text-sm text-gray-400">
                        © 2026 홈시그널AI. All rights reserved.
                      </p>
                    </div>
                    <p className="text-xs text-gray-500 text-center">
                      본 서비스는 투자 권유가 아니며 정보 제공 목적입니다.
                    </p>
                  </div>
                </div>
              </footer>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}
