import { useState, useEffect } from 'react'
import { Users, DollarSign, Zap, UserPlus, TrendingUp, Activity } from 'lucide-react'

interface AdminStats {
  total_users: number
  new_users_this_week: number
  verified_users: number
  admin_users: number
  total_ai_calls: number
  total_ai_cost: number
  recent_signups: {
    id: string
    email: string
    name: string | null
    created_at: string
    is_verified: boolean
  }[]
}

export function AdminOverview() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('session_token')
      const response = await fetch('/api/admin/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) {
        throw new Error('Failed to fetch admin stats')
      }
      const data = await response.json()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#1E3A5F' }}></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  const statCards = [
    { label: 'Total Users', value: stats?.total_users || 0, icon: Users, color: '#1E3A5F' },
    { label: 'New This Week', value: stats?.new_users_this_week || 0, icon: UserPlus, color: '#059669' },
    { label: 'Verified Users', value: stats?.verified_users || 0, icon: Activity, color: '#7C3AED' },
    { label: 'Total AI Calls', value: stats?.total_ai_calls || 0, icon: Zap, color: '#D97706' },
    { label: 'Total AI Cost', value: `$${(stats?.total_ai_cost || 0).toFixed(2)}`, icon: DollarSign, color: '#DC2626' },
    { label: 'Admin Users', value: stats?.admin_users || 0, icon: TrendingUp, color: '#0891B2' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>Admin Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-lg p-5 border" style={{ borderColor: '#E5E7EB' }}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold" style={{ color: stat.color }}>{stat.value}</p>
                </div>
                <div className="p-3 rounded-lg" style={{ backgroundColor: `${stat.color}10` }}>
                  <Icon className="w-6 h-6" style={{ color: stat.color }} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      <div className="bg-white rounded-lg border" style={{ borderColor: '#E5E7EB' }}>
        <div className="p-4 border-b" style={{ borderColor: '#E5E7EB' }}>
          <h2 className="text-lg font-bold" style={{ color: '#1E3A5F' }}>Recent Signups</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Email</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ divideColor: '#E5E7EB' }}>
              {stats?.recent_signups && stats.recent_signups.length > 0 ? (
                stats.recent_signups.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{user.email}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.name || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        user.is_verified 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {user.is_verified ? 'Verified' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    No recent signups
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
