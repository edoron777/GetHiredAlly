export interface User {
  id: string
  email: string
  name: string | null
  profile_name: string | null
  is_verified?: boolean
  is_admin?: boolean
}

export function getAuthToken(): string | null {
  return localStorage.getItem('auth_token')
}

export function getUser(): User | null {
  const userStr = localStorage.getItem('user')
  if (!userStr) return null
  try {
    return JSON.parse(userStr) as User
  } catch {
    return null
  }
}

export function isAuthenticated(): boolean {
  return !!getAuthToken()
}

export async function logout(): Promise<boolean> {
  const token = getAuthToken()
  
  if (token) {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      })
    } catch {
    }
  }
  
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
  
  return true
}

export function setAuth(token: string, user: User): void {
  localStorage.setItem('auth_token', token)
  localStorage.setItem('user', JSON.stringify(user))
}
