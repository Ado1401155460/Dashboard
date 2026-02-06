const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const fetcher = async (url: string) => {
  const res = await fetch(`${API_URL}${url}`)
  if (!res.ok) {
    throw new Error('请求失败')
  }
  return res.json()
}

export const api = {
  // 挂单相关
  getPendingOrders: () => fetcher('/api/orders/pending'),
  getPendingOrderDetail: (intentId: string) => fetcher(`/api/orders/pending/${intentId}`),
  
  // 头寸相关
  getOpenPositions: () => fetcher('/api/positions/open'),
  getPositionDetail: (intentId: string) => fetcher(`/api/positions/open/${intentId}`),
  
  // 分析相关
  getAccountStats: () => fetcher('/api/analytics/stats'),
  getEquityCurve: () => fetcher('/api/analytics/equity-curve'),
}

