import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export function VerifyEmailPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const emailFromParams = searchParams.get('email') || ''
  const codeFromParams = searchParams.get('code') || ''
  
  const [email, setEmail] = useState(emailFromParams)
  const [code, setCode] = useState(codeFromParams)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const [autoVerified, setAutoVerified] = useState(false)

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendCooldown])

  useEffect(() => {
    if (emailFromParams && codeFromParams && codeFromParams.length === 6 && !autoVerified) {
      setAutoVerified(true)
      handleAutoVerify(emailFromParams, codeFromParams)
    }
  }, [emailFromParams, codeFromParams])

  const handleAutoVerify = async (emailVal: string, codeVal: string) => {
    setIsSubmitting(true)
    try {
      const response = await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailVal.toLowerCase(), code: codeVal })
      })
      const data = await response.json()
      if (!response.ok) {
        setError(data.detail || 'Verification failed')
        return
      }
      setSuccess(data.message || 'Email verified successfully!')
      setTimeout(() => navigate('/login'), 2000)
    } catch {
      setError('Network error. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (!code || code.length !== 6) {
      setError('Please enter a 6-digit verification code')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.toLowerCase(), code })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Verification failed')
        return
      }

      setSuccess(data.message || 'Email verified successfully!')
      setTimeout(() => navigate('/login'), 2000)

    } catch {
      setError('Network error. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/auth/send-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.toLowerCase() })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Failed to resend code')
        return
      }

      setSuccess('A new verification code has been sent to your email')
      setResendCooldown(60)

    } catch {
      setError('Network error. Please try again.')
    }
  }

  return (
    <div className="flex items-center justify-center p-4" style={{ minHeight: 'calc(100vh - 64px)' }}>
      <div className="w-full max-w-md">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
              Verify Your Email
            </h1>
            <p className="text-sm mt-2" style={{ color: '#333333' }}>
              We sent a verification code to
            </p>
            <p className="text-sm font-medium mt-1" style={{ color: '#1E3A5F' }}>
              {email || 'your email'}
            </p>
          </div>

          {success && (
            <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200">
              <p className="text-green-800 text-sm text-center">{success}</p>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200">
              <p className="text-red-800 text-sm text-center">{error}</p>
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-5">
            {!emailFromParams && (
              <div className="space-y-2">
                <Label htmlFor="email" style={{ color: '#333333' }}>Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="code" style={{ color: '#333333' }}>Verification Code</Label>
              <Input
                id="code"
                type="text"
                placeholder="Enter 6-digit code"
                value={code}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '').slice(0, 6)
                  setCode(val)
                }}
                maxLength={6}
                className="text-center text-2xl tracking-widest"
                autoComplete="one-time-code"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              style={{ backgroundColor: '#1E3A5F' }}
              disabled={code.length !== 6 || isSubmitting}
            >
              {isSubmitting ? 'Verifying...' : 'Verify Email'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm" style={{ color: '#333333' }}>
              Didn't receive the code?{' '}
              {resendCooldown > 0 ? (
                <span className="text-gray-500">Resend in {resendCooldown}s</span>
              ) : (
                <button
                  onClick={handleResend}
                  className="font-medium hover:underline"
                  style={{ color: '#1E3A5F' }}
                >
                  Resend code
                </button>
              )}
            </p>
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm" style={{ color: '#333333' }}>
              <button
                onClick={() => navigate('/login')}
                className="font-medium hover:underline"
                style={{ color: '#1E3A5F' }}
              >
                Back to Login
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
