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
  "Identifying potential focus areas...",
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
      } else {
        setJobSource('paste')
      }
      
      setLoading(false)
    }).catch(() => {
      setLoading(false)
      setJobSource('paste')
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
      setCvText('')
    }
  }

  const canGenerate = () => {
    if (!eligible) return false
    
    if (jobSource === 'xray' && !selectedXrayId) return false
    if (jobSource === 'paste' && jobDescription.trim().length < 50) return false
    
    if (cvSource === 'paste' && cvText.trim().length < 50) return false
    if (cvSource === 'upload' && !cvFile) return false
    
    return true
  }

  const handleGenerate = async () => {
    if (!canGenerate()) return
    
    setGenerating(true)
    setError(null)
    setLoadingMessageIndex(0)
    
    const token = getAuthToken()
    if (!token) {
      setError('Please log in to continue')
      setGenerating(false)
      return
    }

    try {
      let cvContent = ''
      
      if (cvSource === 'paste') {
        cvContent = cvText
      } else if (cvSource === 'upload' && cvFile) {
        if (cvFile.type === 'text/plain') {
          cvContent = await cvFile.text()
        } else {
          const formData = new FormData()
          formData.append('file', cvFile)
          formData.append('token', token)
          
          const parseRes = await fetch('/api/cv/parse', {
            method: 'POST',
            body: formData
          })
          
          if (parseRes.ok) {
            const parseData = await parseRes.json()
            cvContent = parseData.text || ''
          }
        }
      }

      const requestBody: Record<string, string> = {
        token,
        provider: selectedProvider
      }
      
      if (jobSource === 'xray') {
        requestBody.xray_analysis_id = selectedXrayId
      } else {
        requestBody.job_description = jobDescription
      }
      
      if (cvContent) {
        requestBody.cv_text = cvContent
      }

      const response = await fetch('/api/smart-questions/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to generate questions')
      }

      const result = await response.json()
      navigate(`/service/predict-questions/smart/results/${result.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (generating) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-lg text-gray-700">{loadingMessages[loadingMessageIndex]}</p>
          <p className="text-sm text-gray-500 mt-2">This may take up to 30 seconds</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] py-8 px-4" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => navigate('/service/predict-questions')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-6"
        >
          <ChevronRight className="h-4 w-4 rotate-180" />
          Back to Questions Service
        </button>

        <div className="bg-white rounded-xl shadow-sm p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="h-8 w-8 text-purple-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Smart Questions</h1>
            <p className="text-gray-600">
              Get personalized interview questions based on the job and your background
            </p>
          </div>

          {!eligible && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <Lock className="h-5 w-5 text-amber-600 mt-0.5" />
                <div>
                  <p className="font-medium text-amber-800">Access Limited</p>
                  <p className="text-sm text-amber-700 mt-1">{eligibilityReason}</p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Job Description Source
              </label>
              <div className="flex gap-3">
                <button
                  onClick={() => setJobSource('xray')}
                  disabled={xrayAnalyses.length === 0}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    jobSource === 'xray'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${xrayAnalyses.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <FileText className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm">From X-Ray Analysis</span>
                </button>
                <button
                  onClick={() => setJobSource('paste')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    jobSource === 'paste'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <FileText className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm">Paste Job Description</span>
                </button>
              </div>
            </div>

            {jobSource === 'xray' && xrayAnalyses.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Analysis
                </label>
                <select
                  value={selectedXrayId}
                  onChange={(e) => setSelectedXrayId(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {xrayAnalyses.map((analysis) => (
                    <option key={analysis.id} value={analysis.id}>
                      {analysis.job_title}
                      {analysis.company_name ? ` at ${analysis.company_name}` : ''} - {new Date(analysis.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {jobSource === 'paste' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the full job description here..."
                  rows={6}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {jobDescription.length < 50 ? `Need at least 50 characters (${jobDescription.length}/50)` : `${jobDescription.length} characters`}
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Your CV/Resume (Optional but Recommended)
              </label>
              <div className="flex gap-3">
                <button
                  onClick={() => setCvSource('none')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    cvSource === 'none'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <span className="text-sm">Skip CV</span>
                </button>
                <button
                  onClick={() => setCvSource('upload')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    cvSource === 'upload'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Upload className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm">Upload CV</span>
                </button>
                <button
                  onClick={() => setCvSource('paste')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    cvSource === 'paste'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <FileText className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm">Paste CV</span>
                </button>
              </div>
            </div>

            {cvSource === 'upload' && (
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors"
                >
                  {cvFile ? (
                    <div className="text-center">
                      <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                      <p className="text-sm text-gray-700">{cvFile.name}</p>
                      <p className="text-xs text-gray-500 mt-1">Click to change file</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-600">Click to upload PDF, DOCX, or TXT</p>
                    </div>
                  )}
                </button>
              </div>
            )}

            {cvSource === 'paste' && (
              <div>
                <textarea
                  value={cvText}
                  onChange={(e) => setCvText(e.target.value)}
                  placeholder="Paste your CV/resume content here..."
                  rows={6}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {cvText.length < 50 ? `Need at least 50 characters (${cvText.length}/50)` : `${cvText.length} characters`}
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Provider
              </label>
              <AIProviderSelector
                selectedProvider={selectedProvider}
                onProviderChange={setSelectedProvider}
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={!canGenerate()}
              className={`w-full py-4 rounded-lg font-medium text-white transition-all ${
                canGenerate()
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-gray-300 cursor-not-allowed'
              }`}
            >
              <Sparkles className="h-5 w-5 inline-block mr-2" />
              Generate Smart Questions
            </button>

            {!freeTrialUsed && eligible && (
              <p className="text-center text-sm text-gray-500 flex items-center justify-center gap-1">
                <Sparkles className="h-4 w-4" />
                This will use your 1 free analysis
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
