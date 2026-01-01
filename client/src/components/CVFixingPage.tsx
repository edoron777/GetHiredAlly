import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Wrench } from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { GHAScanner, playStartSound, playCompleteSound } from '@/components/common/GHAScanner'

const FIX_STATUS_MESSAGES = [
  'Analyzing issues...',
  'Applying grammar corrections...',
  'Strengthening action verbs...',
  'Adding quantified achievements...',
  'Optimizing formatting...',
  'Enhancing professional language...',
  'Polishing final details...',
  'Almost done...'
]

export function CVFixingPage() {
  const navigate = useNavigate()
  const { scanId } = useParams<{ scanId: string }>()

  const [progress, setProgress] = useState(0)
  const [currentMessage, setCurrentMessage] = useState(0)
  const [fixComplete, setFixComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    if (!scanId) {
      navigate('/service/cv-optimizer')
    }
  }, [navigate, scanId])

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % FIX_STATUS_MESSAGES.length)
    }, 2500)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90 && !fixComplete) return 90
        if (fixComplete) return Math.min(prev + 5, 100)
        return prev + Math.random() * 3
      })
    }, 200)
    return () => clearInterval(interval)
  }, [fixComplete])

  useEffect(() => {
    if (!scanId) return

    const runFix = async () => {
      try {
        const token = getAuthToken()
        const response = await fetch(`/api/cv-optimizer/fix/${scanId}?token=${token}`, {
          method: 'POST'
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Fix failed')
        }

        setFixComplete(true)
        playCompleteSound()

        setTimeout(() => {
          navigate(`/service/cv-optimizer/fixed/${scanId}`)
        }, 2000)

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Fix failed. Please try again.')
      }
    }

    playStartSound()
    setTimeout(runFix, 1000)
  }, [scanId, navigate])

  if (error) {
    return (
      <div className="min-h-screen bg-[#FAF9F7] flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">⚠️</span>
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Fix Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate(`/service/cv-optimizer/unified?cv_id=${scanId}`)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-blue-500/20 text-blue-300 px-4 py-2 rounded-full mb-4">
            <Wrench className="w-4 h-4" />
            <span className="text-sm font-medium">Auto-Fix in Progress</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Optimizing Your CV
          </h1>
          <p className="text-slate-400">
            AI is applying improvements to make your CV stand out
          </p>
        </div>

        <GHAScanner progress={progress} />

        <div className="mt-8 text-center">
          <p className="text-lg text-white font-medium animate-pulse">
            {FIX_STATUS_MESSAGES[currentMessage]}
          </p>
          <div className="mt-4 w-full max-w-md mx-auto">
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-slate-500 text-sm mt-2">{Math.round(progress)}% complete</p>
          </div>
        </div>

        {fixComplete && (
          <div className="mt-8 text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 bg-green-500/20 text-green-300 px-6 py-3 rounded-full">
              <span className="text-xl">✓</span>
              <span className="font-medium">CV Optimized Successfully!</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
