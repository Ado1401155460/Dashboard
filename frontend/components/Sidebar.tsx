'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Package, TrendingUp, BarChart3, Home, Settings } from 'lucide-react'

const navigation = [
  { name: '首页', href: '/', icon: Home },
  { name: '挂单模块', href: '/orders', icon: Package },
  { name: '头寸模块', href: '/positions', icon: TrendingUp },
  { name: '交易分析', href: '/analytics', icon: BarChart3 },
  { name: 'API设置', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass-effect border-r border-dark-700 p-6 z-50">
      <div className="mb-8">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          量化交易
        </h1>
        <p className="text-sm text-dark-400 mt-1">分析仪表盘</p>
      </div>

      <nav className="space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-blue-500/30'
                  : 'text-dark-400 hover:text-white hover:bg-dark-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-6 left-6 right-6">
        <div className="glass-effect rounded-xl p-4 border border-dark-700">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-dark-400">系统状态</span>
          </div>
          <p className="text-xs text-dark-500">OANDA 连接正常</p>
        </div>
      </div>
    </aside>
  )
}

