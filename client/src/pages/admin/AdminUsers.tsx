import { useState, useEffect } from 'react'
import { Search, Trash2, Shield, ShieldOff, Check, X, ChevronLeft, ChevronRight } from 'lucide-react'
import { getUser } from '@/lib/auth'

interface User {
  id: string
  email: string
  name: string | null
  role: string
  profile_id: string | null
  is_admin: boolean
  is_verified: boolean
  google_id: string | null
  created_at: string
}

interface UsersResponse {
  users: User[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export function AdminUsers() {
  const currentUser = getUser()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [deleteModal, setDeleteModal] = useState<User | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const LIMIT = 15

  useEffect(() => {
    fetchUsers()
  }, [page, search])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: LIMIT.toString(),
      })
      if (search) params.append('search', search)
      
      const response = await fetch(`/api/admin/users?${params}`)
      if (!response.ok) throw new Error('Failed to fetch users')
      
      const data: UsersResponse = await response.json()
      setUsers(data.users)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchUsers()
  }

  const toggleAdmin = async (user: User) => {
    if (user.id === currentUser?.id) return
    
    setActionLoading(user.id)
    try {
      const response = await fetch(`/api/admin/users/${user.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_admin: !user.is_admin })
      })
      if (!response.ok) throw new Error('Failed to update user')
      
      setUsers(users.map(u => 
        u.id === user.id ? { ...u, is_admin: !u.is_admin } : u
      ))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update user')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    
    setActionLoading(deleteModal.id)
    try {
      const response = await fetch(`/api/admin/users/${deleteModal.id}`, {
        method: 'DELETE'
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to delete user')
      }
      
      setUsers(users.filter(u => u.id !== deleteModal.id))
      setDeleteModal(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete user')
    } finally {
      setActionLoading(null)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const isProtectedAdmin = (email: string) => {
    return email === 'edoron777+admin@gmail.com'
  }

  if (loading && users.length === 0) {
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

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>User Management</h1>
        <span className="text-sm text-gray-500">{total} total users</span>
      </div>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by email or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
              style={{ borderColor: '#E5E7EB', focusRing: '#1E3A5F' }}
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg text-white font-medium"
            style={{ backgroundColor: '#1E3A5F' }}
          >
            Search
          </button>
        </div>
      </form>
      
      <div className="bg-white rounded-lg border overflow-hidden" style={{ borderColor: '#E5E7EB' }}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Email</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Role</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Verified</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Admin</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Joined</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y" style={{ divideColor: '#E5E7EB' }}>
              {users.map((user) => {
                const isSelf = user.id === currentUser?.id
                const isProtected = isProtectedAdmin(user.email)
                
                return (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-900">{user.email}</span>
                        {user.google_id && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">Google</span>
                        )}
                        {isProtected && (
                          <span className="text-xs bg-blue-600 text-white px-1.5 py-0.5 rounded">Protected</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.name || '-'}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                        user.role === 'vip' ? 'bg-purple-100 text-purple-700' :
                        user.role === 'special' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {user.role || 'standard'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {user.is_verified ? (
                        <Check className="w-5 h-5 text-green-600 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-gray-400 mx-auto" />
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => toggleAdmin(user)}
                        disabled={isSelf || isProtected || actionLoading === user.id}
                        className={`p-1.5 rounded transition-colors ${
                          isSelf || isProtected ? 'cursor-not-allowed opacity-50' : 'hover:bg-gray-100'
                        }`}
                        title={isSelf ? 'Cannot modify yourself' : isProtected ? 'Protected admin account' : 'Toggle admin status'}
                      >
                        {actionLoading === user.id ? (
                          <div className="w-5 h-5 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: '#1E3A5F', borderTopColor: 'transparent' }}></div>
                        ) : user.is_admin ? (
                          <Shield className="w-5 h-5 text-blue-600" />
                        ) : (
                          <ShieldOff className="w-5 h-5 text-gray-400" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => setDeleteModal(user)}
                        disabled={isSelf || isProtected}
                        className={`p-1.5 rounded transition-colors ${
                          isSelf || isProtected ? 'cursor-not-allowed opacity-50' : 'hover:bg-red-50 text-red-600'
                        }`}
                        title={isSelf ? 'Cannot delete yourself' : isProtected ? 'Protected admin account' : 'Delete user'}
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: '#E5E7EB' }}>
            <p className="text-sm text-gray-600">
              Showing {(page - 1) * LIMIT + 1} to {Math.min(page * LIMIT, total)} of {total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                style={{ borderColor: '#E5E7EB' }}
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                style={{ borderColor: '#E5E7EB' }}
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
      
      {deleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Delete User</h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to delete <strong>{deleteModal.email}</strong>? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteModal(null)}
                className="px-4 py-2 rounded-lg border text-gray-700 hover:bg-gray-50"
                style={{ borderColor: '#E5E7EB' }}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={actionLoading === deleteModal.id}
                className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
              >
                {actionLoading === deleteModal.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
