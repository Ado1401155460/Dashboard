'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import Link from 'next/link'
import { Clock, TrendingUp, TrendingDown, Package, ExternalLink } from 'lucide-react'

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
    { refreshInterval: 5000 }
  )

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
        <div className="glass-effect rounded-xl p-6">
          <div className="h-12 bg-dark-800 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-dark-800 rounded"></div>
            ))}
          </div>
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
      {/* 头部 */}
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

      {/* 列表容器 */}
      {orders && orders.length === 0 ? (
        <div className="glass-effect rounded-xl p-12 text-center">
          <Package className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400 text-lg">暂无挂单</p>
        </div>
      ) : (
        <div className="glass-effect rounded-xl overflow-hidden">
          {/* 表头 */}
          <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-dark-800/50 border-b border-dark-700 text-sm font-semibold text-dark-400">
            <div className="col-span-2">交易对</div>
            <div className="col-span-1 text-center">方向</div>
            <div className="col-span-1 text-right">数量</div>
            <div className="col-span-2 text-right">挂单价</div>
            <div className="col-span-2 text-right">市价</div>
            <div className="col-span-1 text-right">止损</div>
            <div className="col-span-1 text-right">止盈</div>
            <div className="col-span-1 text-center">时间</div>
            <div className="col-span-1 text-center">操作</div>
          </div>

          {/* 列表内容 */}
          <div className="divide-y divide-dark-700">
            {orders?.map((order, index) => (
              <div
                key={order.id}
                className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-dark-800/30 transition-colors"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                {/* 交易对 */}
                <div className="col-span-2 flex flex-col justify-center">
                  <span className="font-bold text-blue-400">{order.symbol}</span>
                  <span className="text-xs text-dark-500 font-mono">
                    {order.intent_id.substring(0, 12)}...
                  </span>
                </div>

                {/* 方向 */}
                <div className="col-span-1 flex items-center justify-center">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    order.units > 0 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {order.units > 0 ? '做多' : '做空'}
                  </span>
                </div>

                {/* 数量 */}
                <div className="col-span-1 flex items-center justify-end">
                  <span className="font-semibold">{Math.abs(order.units).toFixed(0)}</span>
                </div>

                {/* 挂单价 */}
                <div className="col-span-2 flex items-center justify-end">
                  <span className="font-mono font-semibold text-blue-400">
                    {order.entry_price.toFixed(5)}
                  </span>
                </div>

                {/* 市价 */}
                <div className="col-span-2 flex items-center justify-end">
                  <span className="font-mono font-semibold">
                    {order.current_price ? order.current_price.toFixed(5) : '-'}
                  </span>
                </div>

                {/* 止损 */}
                <div className="col-span-1 flex items-center justify-end">
                  <span className="text-sm font-mono text-red-400">
                    {order.stop_loss ? order.stop_loss.toFixed(5) : '-'}
                  </span>
                </div>

                {/* 止盈 */}
                <div className="col-span-1 flex items-center justify-end">
                  <span className="text-sm font-mono text-green-400">
                    {order.take_profit ? order.take_profit.toFixed(5) : '-'}
                  </span>
                </div>

                {/* 时间 */}
                <div className="col-span-1 flex items-center justify-center">
                  <div className="flex flex-col items-center text-xs text-dark-500">
                    <Clock className="w-3 h-3 mb-1" />
                    <span>{new Date(order.created_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>

                {/* 操作 */}
                <div className="col-span-1 flex items-center justify-center">
                  <Link
                    href={`/orders/${order.intent_id}`}
                    className="flex items-center space-x-1 px-3 py-1 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors text-sm"
                  >
                    <span>详情</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
