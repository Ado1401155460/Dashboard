import Link from 'next/link'
import { TrendingUp, Package, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          量化交易分析仪表盘
        </h1>
        <p className="text-dark-400 text-lg">
          实时监控 OANDA 交易所订单数据与 AI 分析报告
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/orders" className="group">
          <div className="glass-effect rounded-2xl p-8 hover:scale-105 transition-all duration-300 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-blue-500/20 rounded-xl group-hover:bg-blue-500/30 transition-colors">
                <Package className="w-8 h-8 text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">挂单模块</h3>
                <p className="text-dark-400 mt-1">未成交的限价单</p>
              </div>
            </div>
          </div>
        </Link>

        <Link href="/positions" className="group">
          <div className="glass-effect rounded-2xl p-8 hover:scale-105 transition-all duration-300 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-purple-500/20 rounded-xl group-hover:bg-purple-500/30 transition-colors">
                <TrendingUp className="w-8 h-8 text-purple-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">头寸模块</h3>
                <p className="text-dark-400 mt-1">已成交的订单</p>
              </div>
            </div>
          </div>
        </Link>

        <Link href="/analytics" className="group">
          <div className="glass-effect rounded-2xl p-8 hover:scale-105 transition-all duration-300 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-green-500/20 rounded-xl group-hover:bg-green-500/30 transition-colors">
                <BarChart3 className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">交易分析</h3>
                <p className="text-dark-400 mt-1">账户统计与收益曲线</p>
              </div>
            </div>
          </div>
        </Link>
      </div>

      <div className="glass-effect rounded-2xl p-8 mt-8">
        <h2 className="text-2xl font-semibold mb-4">系统特性</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              <span className="text-dark-300">实时同步 OANDA 交易数据</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
              <span className="text-dark-300">AI 驱动的交易分析报告</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-dark-300">完整的交易绩效统计</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
              <span className="text-dark-300">收益曲线可视化</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-400 rounded-full"></div>
              <span className="text-dark-300">风险管理指标监控</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-indigo-400 rounded-full"></div>
              <span className="text-dark-300">订单详情深度分析</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

