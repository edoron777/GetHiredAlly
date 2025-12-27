import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { MessageCircle, Sparkles, Lock } from 'lucide-react'

export function QuestionsServicePage() {
  const navigate = useNavigate()
  const [eligible, setEligible] = useState(true)
  const [freeTrialUsed, setFreeTrialUsed] = useState(false)
  const [checkingEligibility, setCheckingEligibility] = useState(true)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const token = getAuthToken()
    if (!token) return

    fetch(`/api/smart-questions/check-eligibility?token=${encodeURIComponent(token)}`)
      .then(res => res.json())
      .then(data => {
        setEligible(data.eligible)
        setFreeTrialUsed(data.free_trial_used)
        setCheckingEligibility(false)
      })
      .catch(() => {
        setCheckingEligibility(false)
      })
  }, [navigate])

  const containerStyle = {
    border: '1px solid #E5E7EB',
    borderRadius: '12px',
    padding: '24px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    height: '100%',
    display: 'flex',
    flexDirection: 'column' as const
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-4 md:p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto">
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="mb-6 text-sm transition-colors"
          style={{ color: '#6B7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#1E3A5F'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
        >
          ← Back to Dashboard
        </button>

        <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
          Prepare for Questions
        </h1>
        <p className="text-lg mb-8" style={{ color: '#6B7280' }}>
          Master the questions interviewers will ask you
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            style={containerStyle}
            onClick={() => navigate('/service/predict-questions/common')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#1E3A5F'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(30, 58, 95, 0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#E5E7EB'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ 
              width: '56px', 
              height: '56px', 
              borderRadius: '12px', 
              backgroundColor: '#E8F0F5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px'
            }}>
              <MessageCircle style={{ width: '28px', height: '28px', color: '#1E3A5F' }} />
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#1E3A5F', marginBottom: '8px' }}>
              Common Interview Questions
            </h2>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '20px', lineHeight: 1.6, flex: 1 }}>
              54 most asked questions with expert tips, answer frameworks, and examples of what to say and avoid.
            </p>
            <button
              type="button"
              style={{
                backgroundColor: '#1E3A5F',
                color: 'white',
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer'
              }}
            >
              Browse Questions
            </button>
          </div>

          <div 
            style={{
              ...containerStyle,
              cursor: eligible ? 'pointer' : 'pointer',
              opacity: 1
            }}
            onClick={() => navigate('/service/predict-questions/smart')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#7C3AED'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(124, 58, 237, 0.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#E5E7EB'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ 
                width: '56px', 
                height: '56px', 
                borderRadius: '12px', 
                backgroundColor: '#F3E8FF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Sparkles style={{ width: '28px', height: '28px', color: '#7C3AED' }} />
              </div>
              {!checkingEligibility && (
                <span 
                  style={{ 
                    padding: '4px 10px', 
                    borderRadius: '9999px', 
                    fontSize: '12px', 
                    fontWeight: 500,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    backgroundColor: eligible && !freeTrialUsed ? '#E9D5FF' : '#FEE2E2',
                    color: eligible && !freeTrialUsed ? '#7C3AED' : '#991B1B'
                  }}
                >
                  {eligible && !freeTrialUsed ? (
                    <>
                      <Sparkles style={{ width: '12px', height: '12px' }} />
                      1 Free Analysis
                    </>
                  ) : (
                    <>
                      <Lock style={{ width: '12px', height: '12px' }} />
                      Upgrade Required
                    </>
                  )}
                </span>
              )}
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#1E3A5F', marginBottom: '8px' }}>
              Smart Questions Predictor
            </h2>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '20px', lineHeight: 1.6, flex: 1 }}>
              AI-predicted questions based on your specific job description and CV. Get personalized preparation for your interview.
            </p>
            <button
              type="button"
              style={{
                backgroundColor: eligible ? '#7C3AED' : '#1E3A5F',
                color: 'white',
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              {eligible && !freeTrialUsed ? (
                <>
                  <Sparkles style={{ width: '14px', height: '14px' }} />
                  Try Free
                </>
              ) : (
                'Upgrade - $4.99'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
