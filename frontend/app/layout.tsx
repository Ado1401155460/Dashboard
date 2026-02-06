import type { Metadata } from 'next'
import { Outfit } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/Sidebar'

const outfit = Outfit({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '量化交易分析仪表盘',
  description: 'OANDA 量化交易数据分析与监控系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={outfit.className}>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 ml-64 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

