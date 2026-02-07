'use client'

import { useState, useEffect } from 'react'
import { Settings, Plus, Edit2, Trash2, Power, Check, X, Eye, EyeOff } from 'lucide-react'

interface ApiConfig {
  id: number
  exchange_name: string
  api_url: string
  account_id: string | null
  api_key: string | null
  api_secret: string | null
  access_token: string | null
  is_active: number
  is_testnet: number
  extra_config: any
  created_at: string
  updated_at: string
}

export default function ApiSettingsPage() {
  const [configs, setConfigs] = useState<ApiConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showSecrets, setShowSecrets] = useState<{ [key: number]: boolean }>({})
  
  const [formData, setFormData] = useState({
    exchange_name: 'OANDA',
    api_url: 'https://api-fxpractice.oanda.com',
    account_id: '',
    api_key: '',
    api_secret: '',
    access_token: '',
    is_active: 1,
    is_testnet: 0,
    extra_config: {}
  })

  useEffect(() => {
    fetchConfigs()
  }, [])

  const fetchConfigs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/config/`)
      const data = await response.json()
      setConfigs(data)
    } catch (error) {
      console.error('获取配置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const url = editingId 
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/config/${editingId}`
        : `${process.env.NEXT_PUBLIC_API_URL}/api/config/`
      
      const method = editingId ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        await fetchConfigs()
        resetForm()
      }
    } catch (error) {
      console.error('保存配置失败:', error)
    }
  }

  const handleEdit = (config: ApiConfig) => {
    setFormData({
      exchange_name: config.exchange_name,
      api_url: config.api_url,
      account_id: config.account_id || '',
      api_key: config.api_key || '',
      api_secret: config.api_secret || '',
      access_token: config.access_token || '',
      is_active: config.is_active,
      is_testnet: config.is_testnet,
      extra_config: config.extra_config || {}
    })
    setEditingId(config.id)
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个配置吗？')) return
    
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/config/${id}`, {
        method: 'DELETE'
      })
      await fetchConfigs()
    } catch (error) {
      console.error('删除配置失败:', error)
    }
  }

  const handleActivate = async (id: number) => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/config/${id}/activate`, {
        method: 'POST'
      })
      await fetchConfigs()
    } catch (error) {
      console.error('激活配置失败:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      exchange_name: 'OANDA',
      api_url: 'https://api-fxpractice.oanda.com',
      account_id: '',
      api_key: '',
      api_secret: '',
      access_token: '',
      is_active: 1,
      is_testnet: 0,
      extra_config: {}
    })
    setEditingId(null)
    setShowForm(false)
  }

  const toggleSecretVisibility = (id: number) => {
    setShowSecrets(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const maskSecret = (secret: string | null, id: number) => {
    if (!secret) return '-'
    if (showSecrets[id]) return secret
    return '••••••••••••••••'
  }

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
        <div className="glass-effect rounded-xl p-6">
          <div className="h-12 bg-dark-800 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-dark-800 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-3">
            <Settings className="w-8 h-8 text-yellow-400" />
            <span>API 设置</span>
          </h1>
          <p className="text-dark-400 mt-1">管理交易所 API 配置，支持多交易所切换</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center space-x-2 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg transition-colors"
        >
          {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
          <span>{showForm ? '取消' : '添加配置'}</span>
        </button>
      </div>

      {/* 表单 */}
      {showForm && (
        <div className="glass-effect rounded-xl p-6 border-2 border-yellow-500/30">
          <h2 className="text-xl font-bold mb-4">
            {editingId ? '编辑配置' : '新增配置'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  交易所名称 *
                </label>
                <input
                  type="text"
                  value={formData.exchange_name}
                  onChange={(e) => setFormData({ ...formData, exchange_name: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="OANDA, Binance, etc."
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  API URL *
                </label>
                <input
                  type="url"
                  value={formData.api_url}
                  onChange={(e) => setFormData({ ...formData, api_url: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="https://api-fxpractice.oanda.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  账户 ID
                </label>
                <input
                  type="text"
                  value={formData.account_id}
                  onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="101-001-12345678-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  API Key
                </label>
                <input
                  type="text"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="API Key"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  API Secret
                </label>
                <input
                  type="password"
                  value={formData.api_secret}
                  onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="API Secret"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-400 mb-2">
                  Access Token
                </label>
                <input
                  type="password"
                  value={formData.access_token}
                  onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:border-yellow-500"
                  placeholder="Access Token"
                />
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_testnet === 1}
                    onChange={(e) => setFormData({ ...formData, is_testnet: e.target.checked ? 1 : 0 })}
                    className="w-4 h-4 text-yellow-500 bg-dark-800 border-dark-700 rounded focus:ring-yellow-500"
                  />
                  <span className="text-sm">测试网</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_active === 1}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked ? 1 : 0 })}
                    className="w-4 h-4 text-yellow-500 bg-dark-800 border-dark-700 rounded focus:ring-yellow-500"
                  />
                  <span className="text-sm">启用</span>
                </label>
              </div>
            </div>

            <div className="flex items-center space-x-3 pt-4">
              <button
                type="submit"
                className="flex items-center space-x-2 px-6 py-2 bg-yellow-500 hover:bg-yellow-600 text-dark-900 font-semibold rounded-lg transition-colors"
              >
                <Check className="w-5 h-5" />
                <span>{editingId ? '更新' : '创建'}</span>
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 配置列表 */}
      <div className="glass-effect rounded-xl overflow-hidden">
        <div className="px-6 py-4 bg-dark-800/50 border-b border-dark-700">
          <h2 className="text-lg font-semibold">已保存的配置</h2>
        </div>

        {configs.length === 0 ? (
          <div className="p-12 text-center text-dark-400">
            <Settings className="w-16 h-16 mx-auto mb-4 text-dark-600" />
            <p>暂无配置，请添加一个</p>
          </div>
        ) : (
          <div className="divide-y divide-dark-700">
            {configs.map((config) => (
              <div
                key={config.id}
                className={`p-6 hover:bg-dark-800/30 transition-colors ${
                  config.is_active ? 'bg-yellow-500/5 border-l-4 border-yellow-500' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-xl font-bold text-yellow-400">
                        {config.exchange_name}
                      </h3>
                      {config.is_active === 1 && (
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded-full flex items-center space-x-1">
                          <Power className="w-3 h-3" />
                          <span>激活中</span>
                        </span>
                      )}
                      {config.is_testnet === 1 && (
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-medium rounded-full">
                          测试网
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-dark-400">API URL:</span>
                        <p className="font-mono text-xs mt-1 break-all">{config.api_url}</p>
                      </div>
                      
                      {config.account_id && (
                        <div>
                          <span className="text-dark-400">账户 ID:</span>
                          <p className="font-mono text-xs mt-1">{config.account_id}</p>
                        </div>
                      )}
                      
                      {config.api_key && (
                        <div>
                          <span className="text-dark-400">API Key:</span>
                          <div className="flex items-center space-x-2 mt-1">
                            <p className="font-mono text-xs">{maskSecret(config.api_key, config.id)}</p>
                            <button
                              onClick={() => toggleSecretVisibility(config.id)}
                              className="text-dark-500 hover:text-white"
                            >
                              {showSecrets[config.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      )}
                      
                      {config.access_token && (
                        <div>
                          <span className="text-dark-400">Access Token:</span>
                          <div className="flex items-center space-x-2 mt-1">
                            <p className="font-mono text-xs">{maskSecret(config.access_token, config.id)}</p>
                            <button
                              onClick={() => toggleSecretVisibility(config.id)}
                              className="text-dark-500 hover:text-white"
                            >
                              {showSecrets[config.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="text-xs text-dark-500">
                      创建于: {new Date(config.created_at).toLocaleString('zh-CN')} | 
                      更新于: {new Date(config.updated_at).toLocaleString('zh-CN')}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    {config.is_active === 0 && (
                      <button
                        onClick={() => handleActivate(config.id)}
                        className="p-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors"
                        title="激活"
                      >
                        <Power className="w-5 h-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleEdit(config)}
                      className="p-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors"
                      title="编辑"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(config.id)}
                      className="p-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 说明文档 */}
      <div className="glass-effect rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4 text-yellow-400">📖 使用说明</h2>
        <div className="space-y-3 text-sm text-dark-300">
          <p><strong>1. OANDA 配置示例：</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>交易所名称: OANDA</li>
            <li>API URL (实盘): https://api-fxtrade.oanda.com</li>
            <li>API URL (模拟): https://api-fxpractice.oanda.com</li>
            <li>账户 ID: 从 OANDA 控制台获取</li>
            <li>Access Token: 从 OANDA 控制台生成</li>
          </ul>
          
          <p className="pt-2"><strong>2. 切换交易所：</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>添加新的交易所配置</li>
            <li>点击"激活"按钮切换到该配置</li>
            <li>系统会自动禁用其他配置</li>
          </ul>
          
          <p className="pt-2"><strong>3. 安全提示：</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>API Secret 和 Access Token 会被加密存储</li>
            <li>默认隐藏敏感信息，点击眼睛图标可查看</li>
            <li>建议定期更换 API 密钥</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

