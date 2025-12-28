import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, DollarSign, Activity, CheckCircle, Clock, Zap, AlertCircle } from 'lucide-react'

interface Summary {
  total_requests: number
  successful_requests: number
  success_rate: number
  total_cost: number
  total_tokens: number
  avg_duration_ms: number
}

interface ProviderData {
  provider: string
  cost?: number
  count?: number
}

interface ServiceData {
  service: string
  cost?: number
  count?: number
}

interface DailyData {
  date: string
  cost: number
  requests: number
  tokens: number
}

interface RecentCall {
  id: string
  user_id: string | null
  service_name: string
  provider: string
  model: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  cost_usd: number | null
  duration_ms: number
  success: boolean
  error_message: string | null
  created_at: string
}

interface UserUsage {
  user_id: string
  email: string | null
  total_requests: number
  total_cost: number
  total_input_tokens: number
  total_output_tokens: number
  last_used: string | null
}

interface UsageData {
  period_days: number
  summary: Summary
  cost_by_provider: ProviderData[]
  requests_by_provider: ProviderData[]
  cost_by_service: ServiceData[]
  requests_by_service: ServiceData[]
  daily_trend: DailyData[]
}

export function AdminAIUsagePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [usageData, setUsageData] = useState<UsageData | null>(null)
  const [recentCalls, setRecentCalls] = useState<RecentCall[]>([])
  const [userUsage, setUserUsage] = useState<UserUsage[]>([])
  const [periodDays, setPeriodDays] = useState(30)

  useEffect(() => {
    fetchData()
  }, [periodDays])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('auth_token')
      const headers = { 'Authorization': `Bearer ${token}` }
      
      const [summaryRes, recentRes, userRes] = await Promise.all([
        fetch(`/api/admin/ai-usage/summary?days=${periodDays}`, { headers }),
        fetch('/api/admin/ai-usage/recent?limit=50', { headers }),
        fetch(`/api/admin/ai-usage/by-user?days=${periodDays}&limit=20`, { headers })
      ])
      
      if (!summaryRes.ok || !recentRes.ok) {
        throw new Error('Failed to fetch data')
      }
      
      const summaryData = await summaryRes.json()
      const recentData = await recentRes.json()
      const userData = userRes.ok ? await userRes.json() : { users: [] }
      
      setUsageData(summaryData)
      setRecentCalls(recentData.calls || [])
      setUserUsage(userData.users || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const formatCost = (cost: number) => `$${cost.toFixed(4)}`
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#1E3A5F' }}></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-4 md:p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="h-5 w-5" />
          Back to Dashboard
        </button>

        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>AI Usage Dashboard</h1>
          <select
            value={periodDays}
            onChange={(e) => setPeriodDays(Number(e.target.value))}
            className="px-4 py-2 border rounded-lg bg-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {usageData && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg" style={{ backgroundColor: '#D1FAE5' }}>
                    <DollarSign className="h-5 w-5 text-green-600" />
                  </div>
                  <span className="text-gray-500 text-sm">Total Cost</span>
                </div>
                <div className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
                  {formatCost(usageData.summary.total_cost)}
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg" style={{ backgroundColor: '#DBEAFE' }}>
                    <Activity className="h-5 w-5 text-blue-600" />
                  </div>
                  <span className="text-gray-500 text-sm">Total Requests</span>
                </div>
                <div className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
                  {usageData.summary.total_requests.toLocaleString()}
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg" style={{ backgroundColor: '#FEF3C7' }}>
                    <CheckCircle className="h-5 w-5 text-amber-600" />
                  </div>
                  <span className="text-gray-500 text-sm">Success Rate</span>
                </div>
                <div className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
                  {usageData.summary.success_rate}%
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg" style={{ backgroundColor: '#E0E7FF' }}>
                    <Clock className="h-5 w-5 text-indigo-600" />
                  </div>
                  <span className="text-gray-500 text-sm">Avg Response Time</span>
                </div>
                <div className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
                  {(usageData.summary.avg_duration_ms / 1000).toFixed(1)}s
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-xl p-6 shadow-md">
                <h2 className="text-lg font-semibold mb-4" style={{ color: '#1E3A5F' }}>Cost by Provider</h2>
                <div className="space-y-3">
                  {usageData.cost_by_provider.map((item) => {
                    const percentage = usageData.summary.total_cost > 0 
                      ? ((item.cost || 0) / usageData.summary.total_cost * 100) 
                      : 0
                    return (
                      <div key={item.provider}>
                        <div className="flex justify-between mb-1">
                          <span className="font-medium capitalize">{item.provider}</span>
                          <span className="text-gray-600">{formatCost(item.cost || 0)}</span>
                        </div>
                        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full"
                            style={{ 
                              width: `${percentage}%`,
                              backgroundColor: item.provider === 'claude' ? '#F59E0B' : '#10B981'
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <h2 className="text-lg font-semibold mb-4" style={{ color: '#1E3A5F' }}>Cost by Service</h2>
                <div className="space-y-3">
                  {usageData.cost_by_service.map((item) => {
                    const percentage = usageData.summary.total_cost > 0 
                      ? ((item.cost || 0) / usageData.summary.total_cost * 100) 
                      : 0
                    return (
                      <div key={item.service}>
                        <div className="flex justify-between mb-1">
                          <span className="font-medium capitalize">{item.service.replace('_', ' ')}</span>
                          <span className="text-gray-600">{formatCost(item.cost || 0)}</span>
                        </div>
                        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full"
                            style={{ 
                              width: `${percentage}%`,
                              backgroundColor: item.service === 'xray' ? '#3B82F6' : '#8B5CF6'
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md mb-8">
              <h2 className="text-lg font-semibold mb-4" style={{ color: '#1E3A5F' }}>Cost by User</h2>
              {userUsage.length === 0 ? (
                <div className="text-center text-gray-500 py-8">No user data available for this period</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-gray-50">
                        <th className="text-left py-3 px-4 font-medium text-gray-500 uppercase text-xs">User</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-500 uppercase text-xs">Requests</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-500 uppercase text-xs">Tokens</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-500 uppercase text-xs">Cost</th>
                        <th className="text-right py-3 px-4 font-medium text-gray-500 uppercase text-xs">Last Used</th>
                      </tr>
                    </thead>
                    <tbody>
                      {userUsage.map((userRow, index) => (
                        <tr key={userRow.user_id || index} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div className="font-medium text-gray-900">
                              {userRow.email || 'Unknown User'}
                            </div>
                            <div className="text-xs text-gray-400">
                              {userRow.user_id?.slice(0, 8)}...
                            </div>
                          </td>
                          <td className="py-3 px-4 text-right text-gray-600">
                            {userRow.total_requests || 0}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-600">
                            {((userRow.total_input_tokens || 0) + (userRow.total_output_tokens || 0)).toLocaleString()}
                          </td>
                          <td className="py-3 px-4 text-right font-semibold" style={{ color: '#1E3A5F' }}>
                            {formatCost(userRow.total_cost || 0)}
                          </td>
                          <td className="py-3 px-4 text-right text-gray-500">
                            {userRow.last_used 
                              ? new Date(userRow.last_used).toLocaleDateString()
                              : 'Never'
                            }
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md mb-8">
              <h2 className="text-lg font-semibold mb-4" style={{ color: '#1E3A5F' }}>Daily Trend</h2>
              {usageData.daily_trend.length > 0 ? (
                <div className="overflow-x-auto">
                  <div className="flex gap-1 min-w-fit" style={{ height: '150px' }}>
                    {usageData.daily_trend.slice(-30).map((day) => {
                      const maxCost = Math.max(...usageData.daily_trend.map(d => d.cost), 0.01)
                      const heightPercent = (day.cost / maxCost) * 100
                      return (
                        <div key={day.date} className="flex flex-col items-center justify-end flex-1 min-w-[20px]">
                          <div 
                            className="w-full rounded-t"
                            style={{ 
                              height: `${Math.max(heightPercent, 2)}%`,
                              backgroundColor: '#1E3A5F',
                              minHeight: '4px'
                            }}
                            title={`${day.date}: ${formatCost(day.cost)} (${day.requests} requests)`}
                          />
                          <span className="text-xs text-gray-400 mt-1 transform -rotate-45 origin-top-left">
                            {day.date.slice(5)}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">No data available for this period</div>
              )}
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <h2 className="text-lg font-semibold mb-4" style={{ color: '#1E3A5F' }}>Recent AI Calls</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-2 font-medium text-gray-500">Time</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-500">Service</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-500">Provider</th>
                      <th className="text-right py-3 px-2 font-medium text-gray-500">Tokens</th>
                      <th className="text-right py-3 px-2 font-medium text-gray-500">Cost</th>
                      <th className="text-right py-3 px-2 font-medium text-gray-500">Duration</th>
                      <th className="text-center py-3 px-2 font-medium text-gray-500">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentCalls.map((call) => (
                      <tr key={call.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-2 text-gray-600">{formatDate(call.created_at)}</td>
                        <td className="py-3 px-2">
                          <span className="px-2 py-1 rounded text-xs font-medium"
                            style={{
                              backgroundColor: call.service_name === 'xray' ? '#DBEAFE' : '#E9D5FF',
                              color: call.service_name === 'xray' ? '#1D4ED8' : '#7C3AED'
                            }}
                          >
                            {call.service_name}
                          </span>
                        </td>
                        <td className="py-3 px-2">
                          <span className="flex items-center gap-1">
                            <Zap className="h-3 w-3" style={{ color: call.provider === 'claude' ? '#F59E0B' : '#10B981' }} />
                            <span className="capitalize">{call.provider}</span>
                          </span>
                        </td>
                        <td className="py-3 px-2 text-right text-gray-600">{call.total_tokens?.toLocaleString()}</td>
                        <td className="py-3 px-2 text-right font-medium">{call.cost_usd ? formatCost(call.cost_usd) : '-'}</td>
                        <td className="py-3 px-2 text-right text-gray-600">{(call.duration_ms / 1000).toFixed(1)}s</td>
                        <td className="py-3 px-2 text-center">
                          {call.success ? (
                            <CheckCircle className="h-4 w-4 text-green-500 mx-auto" />
                          ) : (
                            <AlertCircle className="h-4 w-4 text-red-500 mx-auto" title={call.error_message || 'Failed'} />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {recentCalls.length === 0 && (
                  <div className="text-center text-gray-500 py-8">No AI calls recorded yet</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
