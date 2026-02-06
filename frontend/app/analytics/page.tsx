'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Target, Activity, Clock, Award, AlertTriangle } from 'lucide-react'

interface AccountStats {
  total_balance: number
  total_position_value: number
  win_rate: number
  profit_loss_ratio: number
  long_win_rate: number
  short_win_rate: number
  max_drawdown: number
  profit_factor: number
  consecutive_losses: number
  consecutive_wins: number
  avg_holding_time: number
}

interface EquityCurvePoint {
  date: string
  cumulative_profit: number
  balance: number
}

export default function AnalyticsPage() {
  const { data: stats, error: statsError, isLoading: statsLoading } = useSWR<AccountStats>(
    '/api/analytics/stats',
    api.getAccountStats,
    { refreshInterval: 10000 }
  )

  const { data: equityCurve, error: curveError, isLoading: curveLoading } = useSWR<{ data: EquityCurvePoint[] }>(
    '/api/analytics/equity-curve',
    api.getEquityCurve,
    { refreshInterval: 10000 }
  )

  if (statsLoading || curveLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="glass-effect rounded-xl p-6 space-y-3">
              <div className="h-4 bg-dark-800 rounded w-2/3"></div>
              <div className="h-6 bg-dark-800 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (statsError || curveError) {
    return (
      <div className="glass-effect rounded-xl p-8 text-center">
        <p className="text-red-400">加载失败</p>
      </div>
    )
  }

  const chartData = equityCurve?.data.map(point => ({
    date: new Date(point.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    balance: point.balance,
    profit: point.cumulative_profit
  })) || []

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold">交易分析</h1>
        <p className="text-dark-400 mt-1">账户统计与收益曲线</p>
      </div>

      {/* 核心指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-effect rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <DollarSign className="w-6 h-6 text-blue-400" />
            </div>
            <span className="text-xs text-dark-400">账户总资金</span>
          </div>
          <p className="text-3xl font-bold text-blue-400">
            ${stats?.total_balance.toLocaleString() || 0}
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-purple-400" />
            </div>
            <span className="text-xs text-dark-400">总持仓资金</span>
          </div>
          <p className="text-3xl font-bold text-purple-400">
            ${stats?.total_position_value.toLocaleString() || 0}
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6 border border-green-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <Target className="w-6 h-6 text-green-400" />
            </div>
            <span className="text-xs text-dark-400">胜率</span>
          </div>
          <p className="text-3xl font-bold text-green-400">
            {stats?.win_rate.toFixed(1) || 0}%
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6 border border-yellow-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 bg-yellow-500/20 rounded-lg">
              <Award className="w-6 h-6 text-yellow-400" />
            </div>
            <span className="text-xs text-dark-400">盈亏比</span>
          </div>
          <p className="text-3xl font-bold text-yellow-400">
            {stats?.profit_loss_ratio.toFixed(2) || 0}
          </p>
        </div>
      </div>

      {/* 详细统计 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-dark-400 text-sm">做多胜率</span>
          </div>
          <p className="text-2xl font-bold text-green-400">
            {stats?.long_win_rate.toFixed(1) || 0}%
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <span className="text-dark-400 text-sm">做空胜率</span>
          </div>
          <p className="text-2xl font-bold text-red-400">
            {stats?.short_win_rate.toFixed(1) || 0}%
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <span className="text-dark-400 text-sm">最大回撤</span>
          </div>
          <p className="text-2xl font-bold text-orange-400">
            {stats?.max_drawdown.toFixed(2) || 0}%
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span className="text-dark-400 text-sm">利润因子</span>
          </div>
          <p className="text-2xl font-bold text-cyan-400">
            {stats?.profit_factor.toFixed(2) || 0}
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <Award className="w-5 h-5 text-green-400" />
            <span className="text-dark-400 text-sm">连续盈利次数</span>
          </div>
          <p className="text-2xl font-bold text-green-400">
            {stats?.consecutive_wins || 0}
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <span className="text-dark-400 text-sm">连续亏损次数</span>
          </div>
          <p className="text-2xl font-bold text-red-400">
            {stats?.consecutive_losses || 0}
          </p>
        </div>

        <div className="glass-effect rounded-xl p-6 md:col-span-2">
          <div className="flex items-center space-x-2 mb-3">
            <Clock className="w-5 h-5 text-purple-400" />
            <span className="text-dark-400 text-sm">平均持仓时间</span>
          </div>
          <p className="text-2xl font-bold text-purple-400">
            {stats?.avg_holding_time.toFixed(1) || 0} 小时
          </p>
        </div>
      </div>

      {/* 收益曲线 */}
      <div className="glass-effect rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6">收益曲线</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis 
                dataKey="date" 
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `$${value.toLocaleString()}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc'
                }}
                formatter={(value: any) => [`$${value.toLocaleString()}`, '账户余额']}
              />
              <Area 
                type="monotone" 
                dataKey="balance" 
                stroke="#3b82f6" 
                strokeWidth={2}
                fill="url(#colorBalance)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-64 flex items-center justify-center text-dark-400">
            暂无收益数据
          </div>
        )}
      </div>
    </div>
  )
}

