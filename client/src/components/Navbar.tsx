import { useState, useEffect, useRef, useCallback } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { getUser, isAuthenticated, logout, type User } from '@/lib/auth'

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

  return (
    <nav className="bg-white shadow-sm border-b" style={{ borderColor: '#e5e5e5' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center">
            <span className="text-xl font-bold" style={{ color: '#1E3A5F' }}>
              GetHiredAlly
            </span>
          </Link>

          <div className="flex items-center gap-3">
            {isLoggedIn && user ? (
              <>
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
                      {user.is_admin && (
                        <Link
                          to="/admin/ai-usage"
                          className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100"
                          style={{ color: '#1E3A5F' }}
                          onClick={() => setDropdownOpen(false)}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                          AI Usage
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
                <button
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Settings"
                >
                  <svg className="w-5 h-5" style={{ color: '#374151' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              </>
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
