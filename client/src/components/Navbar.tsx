import { useState, useEffect, useRef, useCallback } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { getUser, isAuthenticated, logout, type User } from '@/lib/auth'
import { ExternalLink } from 'lucide-react'

export function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [user, setUser] = useState<User | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const checkAuth = useCallback(() => {
    setIsLoggedIn(isAuthenticated())
    setUser(getUser())
  }, [])

  useEffect(() => {
    checkAuth()
  }, [location.pathname, checkAuth])

  useEffect(() => {
    console.log('=== ADMIN DEBUG ===')
    console.log('Full user object:', user)
    console.log('is_admin:', user?.is_admin)
    console.log('typeof is_admin:', typeof user?.is_admin)
  }, [user])

  useEffect(() => {
    const handleStorageChange = () => checkAuth()
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [checkAuth])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    await logout()
    setIsLoggedIn(false)
    setUser(null)
    setDropdownOpen(false)
    navigate('/')
  }

  const isAdminPage = location.pathname.startsWith('/admin')

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-50" style={{ borderColor: '#e5e5e5' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center">
            <span className="text-xl font-bold" style={{ color: '#1E3A5F' }}>
              GetHiredAlly
            </span>
          </Link>

          {isLoggedIn && user && (
            <div className="hidden md:flex items-center gap-2">
              <Link
                to="/dashboard"
                className="px-3 py-2 text-sm font-medium rounded transition-colors"
                style={{
                  backgroundColor: location.pathname === '/dashboard' ? '#1E3A5F' : 'transparent',
                  color: location.pathname === '/dashboard' ? 'white' : '#374151'
                }}
                onMouseEnter={(e) => {
                  if (location.pathname !== '/dashboard') {
                    e.currentTarget.style.backgroundColor = '#f3f4f6'
                  }
                }}
                onMouseLeave={(e) => {
                  if (location.pathname !== '/dashboard') {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }
                }}
              >
                Home
              </Link>
              
              <a 
                href="https://gethiredally.com"
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-2 text-sm font-medium rounded transition-colors flex items-center gap-1"
                style={{ color: '#374151' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                Blog
                <ExternalLink size={14} />
              </a>

              {user.is_admin && (
                <Link
                  to="/admin/ai-usage"
                  className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded transition-colors"
                  style={{
                    backgroundColor: isAdminPage ? '#991B1B' : '#DC2626',
                    color: 'white'
                  }}
                  onMouseEnter={(e) => {
                    if (!isAdminPage) {
                      e.currentTarget.style.backgroundColor = '#B91C1C'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isAdminPage) {
                      e.currentTarget.style.backgroundColor = '#DC2626'
                    }
                  }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  Admin
                </Link>
              )}
            </div>
          )}

          <div className="flex items-center gap-3">
            {isLoggedIn && user ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <span className="text-sm font-medium hidden sm:inline" style={{ color: '#374151' }}>
                    {user.name || user.email}
                  </span>
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{ backgroundColor: '#1E3A5F' }}
                  >
                    {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                  </div>
                  <svg className="w-4 h-4" style={{ color: '#374151' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border py-1 z-50">
                    <div className="px-4 py-2 border-b">
                      <p className="text-sm font-medium" style={{ color: '#333333' }}>
                        {user.name || 'User'}
                      </p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                    <Link
                      to="/dashboard"
                      className="block px-4 py-2 text-sm hover:bg-gray-100"
                      style={{ color: '#333333' }}
                      onClick={() => setDropdownOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm hover:bg-gray-100"
                      style={{ color: '#333333' }}
                      onClick={() => setDropdownOpen(false)}
                    >
                      Settings
                    </Link>
                    {user.is_admin && (
                      <Link
                        to="/admin/ai-usage"
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100"
                        style={{ color: '#DC2626' }}
                        onClick={() => setDropdownOpen(false)}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        Admin Panel
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                      style={{ color: '#333333' }}
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="outline" size="sm">
                    Login
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm" style={{ backgroundColor: '#1E3A5F' }}>
                    Register
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
