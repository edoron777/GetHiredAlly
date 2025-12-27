import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { Loader2, Upload, FileText, Sparkles, Lock, ChevronRight } from 'lucide-react'
import { AIProviderSelector } from './AIProviderSelector'

type Provider = 'claude' | 'gemini'

interface XRayAnalysis {
  id: string
  job_title: string
  company_name?: string
  created_at: string
}

const loadingMessages = [
  "Analyzing job requirements...",
  "Reviewing your background...",
  "Identifying potential weak areas...",
  "Generating personalized questions...",
  "Almost ready..."
]

export function SmartQuestionsPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const [eligible, setEligible] = useState(true)
  const [freeTrialUsed, setFreeTrialUsed] = useState(false)
  const [eligibilityReason, setEligibilityReason] = useState('')
  
  const [jobSource, setJobSource] = useState<'xray' | 'paste'>('xray')
  const [xrayAnalyses, setXrayAnalyses] = useState<XRayAnalysis[]>([])
  const [selectedXrayId, setSelectedXrayId] = useState<string>('')
  const [jobDescription, setJobDescription] = useState('')
  
  const [cvSource, setCvSource] = useState<'none' | 'upload' | 'paste'>('none')
  const [cvText, setCvText] = useState('')
  const [cvFile, setCvFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedProvider, setSelectedProvider] = useState<Provider>('gemini')

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    
    const token = getAuthToken()
    if (!token) return

    Promise.all([
      fetch(`/api/smart-questions/check-eligibility?token=${encodeURIComponent(token)}`),
      fetch(`/api/xray/analyses?token=${encodeURIComponent(token)}`)
    ]).then(async ([eligRes, xrayRes]) => {
      if (eligRes.ok) {
        const data = await eligRes.json()
        setEligible(data.eligible)
        setFreeTrialUsed(data.free_trial_used)
        setEligibilityReason(data.reason)
      }
      
      if (xrayRes.ok) {
        const data = await xrayRes.json()
        setXrayAnalyses(data.analyses || [])
        if (data.analyses?.length > 0) {
          setSelectedXrayId(data.analyses[0].id)
        } else {
          setJobSource('paste')
        }
      }
      
      setLoading(false)
    }).catch(() => {
      setLoading(false)
    })
  }, [navigate])

  useEffect(() => {
    if (generating) {
      const interval = setInterval(() => {
        setLoadingMessageIndex(prev => (prev + 1) % loadingMessages.length)
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [generating])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setCvFile(file)
    
    if (file.type === 'text/plain') {
      const text = await file.text()
      setCvText(text)
    } else {
      setCvText(`[Uploaded: ${file.name}]`)
    }
  }

  const handleGenerate = async () => {
    const token = getAuthToken()
    if (!token) return

    if (jobSource === 'xray' && !selectedXrayId) {
      setError('Please select an X-Ray analysis')
      return
    }
    if (jobSource === 'paste' && jobDescription.length < 100) {
      setError('Please paste a job description (at least 100 characters)')
      return
    }

    setGenerating(true)
    setError(null)
    setLoadingMessageIndex(0)

    try {
      let finalCvText = ''
      if (cvSource === 'paste') {
        finalCvText = cvText
      } else if (cvSource === 'upload' && cvFile) {
        if (cvFile.type === 'text/plain') {
          finalCvText = await cvFile.text()
        } else {
          finalCvText = cvText
        }
      }

      const response = await fetch('/api/smart-questions/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token,
          xray_analysis_id: jobSource === 'xray' ? selectedXrayId : null,
          job_description: jobSource === 'paste' ? jobDescription : null,
          cv_text: finalCvText || null,
          provider: selectedProvider
        })
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to generate questions')
      }

      const data = await response.json()
      navigate(`/service/predict-questions/smart/results/${data.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setGenerating(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const isFormValid = () => {
    if (jobSource === 'xray') return !!selectedXrayId
    return jobDescription.length >= 100
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#1E3A5F' }} />
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 px-4" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            <Sparkles className="inline h-8 w-8 mr-2" />
            Smart Questions Predictor
          </h1>
          <p className="text-gray-600">
            AI-powered questions personalized for your specific job and background
          </p>
        </div>

        {!eligible ? (
          <div className="bg-white rounded-xl p-8 shadow-md text-center" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
            <Lock className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <h2 className="text-xl font-semibold mb-2" style={{ color: '#1E3A5F' }}>
              You've used your free Smart Analysis
            </h2>
            <p className="text-gray-600 mb-6">
              Upgrade to generate unlimited personalized questions
            </p>
            <button
              disabled
              className="px-8 py-3 rounded-lg text-white font-medium opacity-50 cursor-not-allowed"
              style={{ backgroundColor: '#1E3A5F' }}
            >
              Upgrade - $4.99 (Coming Soon)
            </button>
          </div>
        ) : (
          <>
            {!freeTrialUsed && (
              <div className="mb-6 p-4 rounded-lg flex items-center gap-3" style={{ backgroundColor: '#DBEAFE' }}>
                <Sparkles className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-blue-800">Free Trial - 1 Analysis</span>
              </div>
            )}

            <div className="bg-white rounded-xl p-6 shadow-md mb-6" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold" style={{ backgroundColor: '#1E3A5F' }}>1</div>
                <h2 className="text-lg font-semibold" style={{ color: '#1E3A5F' }}>Select Job</h2>
              </div>

              <div className="space-y-3">
                {xrayAnalyses.length > 0 && (
                  <label
                    className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      jobSource === 'xray' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setJobSource('xray')}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="jobSource"
                        checked={jobSource === 'xray'}
                        onChange={() => setJobSource('xray')}
                        className="w-4 h-4"
                      />
                      <span className="font-medium">Use Previous X-Ray Analysis</span>
                    </div>
                    
                    {jobSource === 'xray' && (
                      <select
                        value={selectedXrayId}
                        onChange={(e) => setSelectedXrayId(e.target.value)}
                        className="mt-3 w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {xrayAnalyses.map(analysis => (
                          <option key={analysis.id} value={analysis.id}>
                            {analysis.job_title}{analysis.company_name ? ` at ${analysis.company_name}` : ''} - {formatDate(analysis.created_at)}
                          </option>
                        ))}
                      </select>
                    )}
                  </label>
                )}

                <label
                  className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    jobSource === 'paste' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setJobSource('paste')}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="jobSource"
                      checked={jobSource === 'paste'}
                      onChange={() => setJobSource('paste')}
                      className="w-4 h-4"
                    />
                    <span className="font-medium">Paste New Job Description</span>
                  </div>
                  
                  {jobSource === 'paste' && (
                    <div className="mt-3" onClick={(e) => e.stopPropagation()}>
                      <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Paste the job description here..."
                        className="w-full h-48 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                      />
                      <div className="text-sm text-gray-500 mt-1">
                        {jobDescription.length} characters {jobDescription.length < 100 && '(minimum 100)'}
                      </div>
                    </div>
                  )}
                </label>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md mb-6" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold" style={{ backgroundColor: '#1E3A5F' }}>2</div>
                <h2 className="text-lg font-semibold" style={{ color: '#1E3A5F' }}>Add Your CV (Optional but Recommended)</h2>
              </div>
              <p className="text-gray-600 text-sm mb-4 ml-11">
                Adding your CV allows us to identify specific gaps and personalize questions to YOUR background
              </p>

              <div className="space-y-3">
                <label
                  className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    cvSource === 'none' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setCvSource('none')}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="cvSource"
                      checked={cvSource === 'none'}
                      onChange={() => setCvSource('none')}
                      className="w-4 h-4"
                    />
                    <span className="font-medium">Skip - Generate questions based on job only</span>
                  </div>
                </label>

                <label
                  className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    cvSource === 'upload' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setCvSource('upload')}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="cvSource"
                      checked={cvSource === 'upload'}
                      onChange={() => setCvSource('upload')}
                      className="w-4 h-4"
                    />
                    <Upload className="h-5 w-5 text-gray-500" />
                    <span className="font-medium">Upload CV</span>
                  </div>
                  
                  {cvSource === 'upload' && (
                    <div className="mt-3 ml-7" onClick={(e) => e.stopPropagation()}>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center gap-2"
                      >
                        <FileText className="h-4 w-4" />
                        {cvFile ? cvFile.name : 'Choose file (.pdf, .doc, .docx, .txt)'}
                      </button>
                    </div>
                  )}
                </label>

                <label
                  className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    cvSource === 'paste' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setCvSource('paste')}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="cvSource"
                      checked={cvSource === 'paste'}
                      onChange={() => setCvSource('paste')}
                      className="w-4 h-4"
                    />
                    <span className="font-medium">Paste CV Text</span>
                  </div>
                  
                  {cvSource === 'paste' && (
                    <div className="mt-3" onClick={(e) => e.stopPropagation()}>
                      <textarea
                        value={cvText}
                        onChange={(e) => setCvText(e.target.value)}
                        placeholder="Paste your CV/resume content here..."
                        className="w-full h-48 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                      />
                    </div>
                  )}
                </label>
              </div>

              <div className="mt-4 p-4 rounded-lg flex items-start gap-3" style={{ backgroundColor: '#DBEAFE' }}>
                <Lock className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-blue-800">
                  <strong>Privacy:</strong> Your CV is used only for this analysis and is NOT stored. 
                  It will be deleted immediately after generating your questions.
                </p>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md mb-6" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold" style={{ backgroundColor: '#1E3A5F' }}>3</div>
                <h2 className="text-lg font-semibold" style={{ color: '#1E3A5F' }}>Choose AI Provider (Optional)</h2>
              </div>
              <AIProviderSelector 
                selectedProvider={selectedProvider}
                onProviderChange={setSelectedProvider}
                service="smart_questions"
              />
            </div>

            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={!isFormValid() || generating}
              className="w-full py-4 rounded-xl text-white font-semibold text-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ 
                backgroundColor: '#1E3A5F',
                boxShadow: generating ? 'none' : '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              {generating ? (
                <>
                  <Loader2 className="h-6 w-6 animate-spin" />
                  {loadingMessages[loadingMessageIndex]}
                </>
              ) : (
                <>
                  <Sparkles className="h-6 w-6" />
                  Generate Smart Questions
                  <ChevronRight className="h-5 w-5" />
                </>
              )}
            </button>

            {!freeTrialUsed && !generating && (
              <p className="text-center text-sm text-gray-500 mt-3 flex items-center justify-center gap-1">
                <Sparkles className="h-4 w-4" />
                This will use your 1 free analysis
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
