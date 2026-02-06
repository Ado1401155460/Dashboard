'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import Link from 'next/link'
import { Clock, TrendingUp, TrendingDown, Package } from 'lucide-react'

interface PendingOrder {
  id: number
  intent_id: string
  symbol: string
  units: number
  entry_price: number
  stop_loss: number | null
  take_profit: number | null
  current_price: number | null
  created_at: string
}

export default function OrdersPage() {
  const { data: orders, error, isLoading } = useSWR<PendingOrder[]>(
    '/api/orders/pending',
    api.getPendingOrders,
    { refreshInterval: 5000 } // 每5秒刷新一次
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

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">挂单模块</h1>
          <p className="text-dark-400 mt-1">未成交的限价单</p>
        </div>
        <div className="glass-effect px-4 py-2 rounded-lg">
          <span className="text-dark-400">总计: </span>
          <span className="text-xl font-bold text-blue-400">{orders?.length || 0}</span>
        </div>
      </div>

      {orders && orders.length === 0 ? (
        <div className="glass-effect rounded-xl p-12 text-center">
          <Package className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400 text-lg">暂无挂单</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {orders?.map((order, index) => (
            <Link
              key={order.id}
              href={`/orders/${order.intent_id}`}
              className="group"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="glass-effect rounded-xl p-6 hover:scale-105 transition-all duration-300 cursor-pointer border border-transparent hover:border-blue-500/30">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-blue-400">{order.symbol}</h3>
                    <p className="text-xs text-dark-500 font-mono mt-1">
                      {order.intent_id.substring(0, 8)}...
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    order.units > 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {order.units > 0 ? '做多' : '做空'}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-dark-400 text-sm">数量</span>
                    <span className="font-semibold">{Math.abs(order.units).toFixed(0)}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-dark-400 text-sm">挂单价</span>
                    <span className="font-mono font-semibold text-blue-400">
                      {order.entry_price.toFixed(5)}
                    </span>
                  </div>

                  {order.current_price && (
                    <div className="flex items-center justify-between">
                      <span className="text-dark-400 text-sm">市价</span>
                      <span className="font-mono font-semibold">
                        {order.current_price.toFixed(5)}
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
                        {order.stop_loss ? order.stop_loss.toFixed(5) : '-'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-4 h-4 text-green-400" />
                        <span className="text-xs text-dark-400">止盈</span>
                      </div>
                      <span className="text-sm font-mono text-green-400">
                        {order.take_profit ? order.take_profit.toFixed(5) : '-'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 pt-2 text-xs text-dark-500">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(order.created_at).toLocaleString('zh-CN')}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-dark-700">
                  <button className="w-full py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors text-sm font-medium">
                    查看详情
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

