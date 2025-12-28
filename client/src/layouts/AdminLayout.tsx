import { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, BarChart3, Settings, ArrowLeft, Shield } from 'lucide-react'
import { getUser, isAuthenticated } from '@/lib/auth'

interface AdminLayoutProps {
  children: ReactNode
}

const navItems = [
  { path: '/admin', label: 'Overview', icon: LayoutDashboard },
  { path: '/admin/users', label: 'Users', icon: Users },
  { path: '/admin/ai-usage', label: 'AI Usage', icon: BarChart3 },
  { path: '/admin/settings', label: 'Settings', icon: Settings },
]

export function AdminLayout({ children }: AdminLayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const user = getUser()
  
  if (!isAuthenticated() || !user?.is_admin) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 rounded text-white"
            style={{ backgroundColor: '#1E3A5F' }}
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-[calc(100vh-120px)]" style={{ backgroundColor: '#FAF9F7' }}>
      <aside className="w-60 border-r bg-white" style={{ borderColor: '#E5E7EB' }}>
        <div className="p-4 border-b" style={{ borderColor: '#E5E7EB' }}>
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5" style={{ color: '#1E3A5F' }} />
            <span className="font-bold" style={{ color: '#1E3A5F' }}>Admin Panel</span>
          </div>
          <div className="text-sm text-gray-600">
            Logged in as:
            <div className="font-medium text-gray-900 truncate">{user.name || user.email}</div>
          </div>
        </div>
        
        <nav className="p-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path === '/admin/ai-usage' && location.pathname.startsWith('/admin/ai-usage'))
            const Icon = item.icon
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-colors ${
                  isActive ? 'text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
                style={isActive ? { backgroundColor: '#1E3A5F' } : {}}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>
        
        <div className="p-2 mt-4 border-t" style={{ borderColor: '#E5E7EB' }}>
          <Link
            to="/dashboard"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to App</span>
          </Link>
        </div>
      </aside>
      
      <main className="flex-1 p-6 overflow-auto">
        {children}
      </main>
    </div>
  )
}
