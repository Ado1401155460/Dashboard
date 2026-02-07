'use client'

import { useParams, useRouter } from 'next/navigation'
import useSWR from 'swr'
import { api } from '@/lib/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ArrowLeft, TrendingUp, TrendingDown, Clock, DollarSign } from 'lucide-react'

interface OrderDetail {
  id: number
  intent_id: string
  symbol: string
  direction: string
  units: number
  order_type: string
  entry_price: number
  current_price: number | null
  exit_price: number | null
  stop_loss: number | null
  take_profit: number | null
  status: string
  ai_article: string | null
  analysisJson: any
  confidence: number | null
  oanda_order_id: string | null
  oanda_trade_id: string | null
  created_at: string
  updated_at: string
}

export default function PositionDetailPage() {
  const params = useParams()
  const router = useRouter()
  const intentId = params.intentId as string

  const { data: position, error, isLoading } = useSWR<OrderDetail>(
    intentId ? `/api/positions/open/${intentId}` : null,
    () => api.getPositionDetail(intentId),
    { refreshInterval: 3000 }
  )

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
        <div className="glass-effect rounded-xl p-8 space-y-4">
          <div className="h-6 bg-dark-800 rounded w-1/2"></div>
          <div className="h-4 bg-dark-800 rounded w-3/4"></div>
          <div className="h-4 bg-dark-800 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (error || !position) {
    return (
      <div className="glass-effect rounded-xl p-8 text-center">
        <p className="text-red-400">加载失败或持仓不存在</p>
        <button
          onClick={() => router.back()}
          className="mt-4 px-6 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg transition-colors"
        >
          返回
        </button>
      </div>
    )
  }

  // 计算未实现盈亏
  let unrealizedPL = 0
  if (position.current_price && position.entry_price) {
    if (position.direction === 'long') {
      unrealizedPL = (position.current_price - position.entry_price) * position.units
    } else {
      unrealizedPL = (position.entry_price - position.current_price) * position.units
    }
  }

  const isProfitable = unrealizedPL >= 0

  return (
    <div className="space-y-6 animate-fade-in">
      <button
        onClick={() => router.back()}
        className="flex items-center space-x-2 text-dark-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>返回头寸列表</span>
      </button>

      <div className="glass-effect rounded-xl p-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-purple-400">{position.symbol}</h1>
            <p className="text-dark-400 mt-1 font-mono text-sm">Intent ID: {position.intent_id}</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className={`px-4 py-2 rounded-full font-medium ${
              position.direction === 'long' 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-red-500/20 text-red-400'
            }`}>
              {position.direction === 'long' ? '做多' : '做空'}
            </div>
            <div className={`px-4 py-2 rounded-full font-bold ${
              isProfitable 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-red-500/20 text-red-400'
            }`}>
              {isProfitable ? '+' : ''}{unrealizedPL.toFixed(2)}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-2">
            <p className="text-dark-400 text-sm">订单类型</p>
            <p className="text-xl font-semibold uppercase">{position.order_type}</p>
          </div>

          <div className="space-y-2">
            <p className="text-dark-400 text-sm">数量</p>
            <p className="text-xl font-semibold">{Math.abs(position.units).toFixed(0)}</p>
          </div>

          <div className="space-y-2">
            <p className="text-dark-400 text-sm">成交价</p>
            <p className="text-xl font-semibold font-mono text-purple-400">
              {position.entry_price.toFixed(5)}
            </p>
          </div>

          {position.current_price && (
            <div className="space-y-2">
              <p className="text-dark-400 text-sm">当前市价</p>
              <p className="text-xl font-semibold font-mono">
                {position.current_price.toFixed(5)}
              </p>
            </div>
          )}

          {position.stop_loss && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <TrendingDown className="w-4 h-4 text-red-400" />
                <p className="text-dark-400 text-sm">止损价</p>
              </div>
              <p className="text-xl font-semibold font-mono text-red-400">
                {position.stop_loss.toFixed(5)}
              </p>
            </div>
          )}

          {position.take_profit && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <p className="text-dark-400 text-sm">止盈价</p>
              </div>
              <p className="text-xl font-semibold font-mono text-green-400">
                {position.take_profit.toFixed(5)}
              </p>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-yellow-400" />
              <p className="text-dark-400 text-sm">未实现盈亏</p>
            </div>
            <p className={`text-xl font-semibold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
              {isProfitable ? '+' : ''}{unrealizedPL.toFixed(2)}
            </p>
          </div>

          {position.confidence && (
            <div className="space-y-2">
              <p className="text-dark-400 text-sm">信心指数</p>
              <p className="text-xl font-semibold text-purple-400">
                {(position.confidence * 100).toFixed(1)}%
              </p>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-dark-400" />
              <p className="text-dark-400 text-sm">开仓时间</p>
            </div>
            <p className="text-sm font-medium">
              {new Date(position.created_at).toLocaleString('zh-CN')}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-dark-400" />
              <p className="text-dark-400 text-sm">更新时间</p>
            </div>
            <p className="text-sm font-medium">
              {new Date(position.updated_at).toLocaleString('zh-CN')}
            </p>
          </div>
        </div>

        {position.oanda_trade_id && (
          <div className="mt-6 pt-6 border-t border-dark-700">
            <p className="text-dark-400 text-sm">OANDA 交易 ID</p>
            <p className="font-mono text-sm mt-1">{position.oanda_trade_id}</p>
          </div>
        )}
      </div>

      {position.ai_article && (
        <div className="glass-effect rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
            <span className="bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              AI 交易分析报告
            </span>
          </h2>
          <div className="prose prose-invert prose-purple max-w-none overflow-hidden">
            <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown-content">
              {position.ai_article}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {position.analysisJson && (
        <div className="glass-effect rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-6">分析数据 (JSON)</h2>
          <pre className="bg-dark-900 rounded-lg p-4 overflow-x-auto text-sm">
            <code className="text-green-400">
              {JSON.stringify(position.analysisJson, null, 2)}
            </code>
          </pre>
        </div>
      )}
    </div>
  )
}

