import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Upload, FileText, Search } from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'

const MAX_FILE_SIZE = 10 * 1024 * 1024
const ALLOWED_EXTENSIONS = ['pdf', 'docx', 'doc', 'txt', 'md', 'rtf', 'odt']

interface TestFile {
  name: string
  size: number
}

export function CVOptimizerPage() {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [testFiles, setTestFiles] = useState<TestFile[]>([])
  const [loadingTestFile, setLoadingTestFile] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  useEffect(() => {
    fetch('/api/cv/dev/test-files')
      .then(res => res.json())
      .then(data => setTestFiles(data.files || []))
      .catch(() => setTestFiles([]))
  }, [])

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const validateAndSetFile = (file: File) => {
    setError(null)

    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!extension || !ALLOWED_EXTENSIONS.includes(extension)) {
      setError('Invalid file type. Please upload PDF, DOCX, DOC, TXT, MD, RTF, or ODT.')
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      setError('File too large. Maximum size is 10MB.')
      return
    }

    setSelectedFile(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const clearFile = () => {
    setSelectedFile(null)
    setError(null)
  }

  const handleTestFileSelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const filename = e.target.value
    if (!filename) return
    
    setLoadingTestFile(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/cv/dev/test-files/${encodeURIComponent(filename)}`)
      if (!response.ok) throw new Error('Failed to fetch test file')
      
      const blob = await response.blob()
      const file = new File([blob], filename, { type: blob.type })
      validateAndSetFile(file)
    } catch (err) {
      setError('Failed to load test file')
    } finally {
      setLoadingTestFile(false)
      e.target.value = ''
    }
  }

  const uploadAndScan = async (file: File) => {
    setIsLoading(true)
    setError(null)

    try {
      const token = getAuthToken()
      const formData = new FormData()
      formData.append('file', file)
      formData.append('token', token || '')

      const uploadResponse = await fetch('/api/cv/upload-for-scan', {
        method: 'POST',
        body: formData
      })

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json()
        throw new Error(errorData.detail || 'Failed to upload file')
      }

      const uploadData = await uploadResponse.json()
      const cvId = uploadData.cv_id

      if (cvId) {
        navigate(`/service/cv-optimizer/scanning?cv_id=${cvId}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.')
      setIsLoading(false)
    }
  }

  const handleStartScan = async () => {
    if (selectedFile) {
      await uploadAndScan(selectedFile)
    }
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-2xl mx-auto">
        <Link
          to="/dashboard"
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </Link>

        <h1 className="text-3xl font-bold mb-3" style={{ color: '#1E3A5F' }}>
          Perfect Your CV
        </h1>
        <p className="text-gray-600 mb-4">
          Get an expert AI review of your CV in seconds. Discover what recruiters really see - and how to improve it.
        </p>
        <ul className="text-gray-600 mb-8 space-y-1 text-sm">
          <li className="flex items-center gap-2">
            <span className="text-green-500">&#10003;</span>
            Find hidden issues before recruiters do
          </li>
          <li className="flex items-center gap-2">
            <span className="text-green-500">&#10003;</span>
            Get actionable suggestions ranked by impact
          </li>
          <li className="flex items-center gap-2">
            <span className="text-green-500">&#10003;</span>
            Optional: Let AI fix your CV automatically
          </li>
        </ul>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div
          className={`
            border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer
            ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
            ${selectedFile ? 'border-green-500 bg-green-50' : ''}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div>
              <FileText size={48} className="mx-auto text-green-500 mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-1">
                {selectedFile.name}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                {formatFileSize(selectedFile.size)}
              </p>
              <button
                onClick={clearFile}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove file
              </button>
            </div>
          ) : (
            <div>
              <Upload size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drag & drop your CV here
              </p>
              <p className="text-gray-500 mb-4">or</p>
              <label className="cursor-pointer">
                <span className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50">
                  Browse Files
                </span>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.docx,.doc,.txt,.md,.rtf,.odt"
                  onChange={handleFileSelect}
                />
              </label>
              <p className="text-sm text-gray-400 mt-4">
                Supported: PDF, DOCX, DOC, TXT, MD, RTF, ODT (Max 10MB)
              </p>
            </div>
          )}
        </div>

        {testFiles.length > 0 && (
          <div className="mt-4 p-3 bg-gray-100 border border-gray-300 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 whitespace-nowrap">
                🧪 Dev: Quick Test
              </span>
              <select
                onChange={handleTestFileSelect}
                disabled={loadingTestFile}
                className="flex-1 text-sm border border-gray-300 rounded px-2 py-1 bg-white"
                defaultValue=""
              >
                <option value="">Select a test CV...</option>
                {testFiles.map(f => (
                  <option key={f.name} value={f.name}>
                    {f.name} ({formatFileSize(f.size)})
                  </option>
                ))}
              </select>
              {loadingTestFile && (
                <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
              )}
            </div>
          </div>
        )}

        <div className="text-center mt-8">
          <button
            onClick={handleStartScan}
            disabled={!selectedFile}
            className={`
              px-8 py-3 rounded-lg font-medium text-lg flex items-center justify-center mx-auto
              ${selectedFile
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            <Search size={20} className="mr-2" />
            Start Scan
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-4"></div>
            <span>Preparing scan...</span>
          </div>
        </div>
      )}
    </div>
  )
}
