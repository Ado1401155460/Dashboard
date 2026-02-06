'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import Link from 'next/link'
import { Clock, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'

interface Position {
  id: number
  intent_id: string
  symbol: string
  direction: string
  units: number
  entry_price: number
  stop_loss: number | null
  take_profit: number | null
  current_price: number | null
  unrealized_pl: number | null
  margin: number | null
  created_at: string
}

export default function PositionsPage() {
  const { data: positions, error, isLoading } = useSWR<Position[]>(
    '/api/positions/open',
    api.getOpenPositions,
    { refreshInterval: 3000 } // 每3秒刷新一次
  )

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass-effect rounded-xl p-6 space-y-4">
              <div className="h-4 bg-dark-800 rounded w-2/3"></div>
              <div className="h-4 bg-dark-800 rounded w-1/2"></div>
              <div className="h-4 bg-dark-800 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-effect rounded-xl p-8 text-center">
        <p className="text-red-400">加载失败: {error.message}</p>
      </div>
    )
  }

  const totalPL = positions?.reduce((sum, pos) => sum + (pos.unrealized_pl || 0), 0) || 0

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">头寸模块</h1>
          <p className="text-dark-400 mt-1">已成交的订单</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="glass-effect px-4 py-2 rounded-lg">
            <span className="text-dark-400">总计: </span>
            <span className="text-xl font-bold text-purple-400">{positions?.length || 0}</span>
          </div>
          <div className={`glass-effect px-4 py-2 rounded-lg ${
            totalPL >= 0 ? 'border border-green-500/30' : 'border border-red-500/30'
          }`}>
            <span className="text-dark-400">未实现盈亏: </span>
            <span className={`text-xl font-bold ${totalPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {totalPL >= 0 ? '+' : ''}{totalPL.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {positions && positions.length === 0 ? (
        <div className="glass-effect rounded-xl p-12 text-center">
          <Activity className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400 text-lg">暂无持仓</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {positions?.map((position, index) => {
            const isProfitable = (position.unrealized_pl || 0) >= 0
            
            return (
              <Link
                key={position.id}
                href={`/positions/${position.intent_id}`}
                className="group"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className={`glass-effect rounded-xl p-6 hover:scale-105 transition-all duration-300 cursor-pointer border ${
                  isProfitable 
                    ? 'border-transparent hover:border-green-500/30' 
                    : 'border-transparent hover:border-red-500/30'
                }`}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-purple-400">{position.symbol}</h3>
                      <p className="text-xs text-dark-500 font-mono mt-1">
                        {position.intent_id.substring(0, 8)}...
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      position.direction === 'long' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {position.direction === 'long' ? '做多' : '做空'}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-dark-400 text-sm">数量</span>
                      <span className="font-semibold">{Math.abs(position.units).toFixed(0)}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-dark-400 text-sm">成交价</span>
                      <span className="font-mono font-semibold text-purple-400">
                        {position.entry_price.toFixed(5)}
                      </span>
                    </div>

                    {position.current_price && (
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400 text-sm">市价</span>
                        <span className="font-mono font-semibold">
                          {position.current_price.toFixed(5)}
                        </span>
                      </div>
                    )}

                    {position.unrealized_pl !== null && (
                      <div className={`flex items-center justify-between p-3 rounded-lg ${
                        isProfitable ? 'bg-green-500/10' : 'bg-red-500/10'
                      }`}>
                        <div className="flex items-center space-x-2">
                          <DollarSign className={`w-4 h-4 ${isProfitable ? 'text-green-400' : 'text-red-400'}`} />
                          <span className="text-sm font-medium">未实现盈亏</span>
                        </div>
                        <span className={`font-bold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
                          {isProfitable ? '+' : ''}{position.unrealized_pl.toFixed(2)}
                        </span>
                      </div>
                    )}

                    {position.margin && (
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400 text-sm">保证金</span>
                        <span className="font-semibold text-yellow-400">
                          {position.margin.toFixed(2)}
                        </span>
                      </div>
                    )}

                    <div className="pt-3 border-t border-dark-700">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-1">
                          <TrendingDown className="w-4 h-4 text-red-400" />
                          <span className="text-xs text-dark-400">止损</span>
                        </div>
                        <span className="text-sm font-mono text-red-400">
                          {position.stop_loss ? position.stop_loss.toFixed(5) : '-'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-1">
                          <TrendingUp className="w-4 h-4 text-green-400" />
                          <span className="text-xs text-dark-400">止盈</span>
                        </div>
                        <span className="text-sm font-mono text-green-400">
                          {position.take_profit ? position.take_profit.toFixed(5) : '-'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 pt-2 text-xs text-dark-500">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(position.created_at).toLocaleString('zh-CN')}</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-dark-700">
                    <button className="w-full py-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 rounded-lg transition-colors text-sm font-medium">
                      查看详情
                    </button>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}

