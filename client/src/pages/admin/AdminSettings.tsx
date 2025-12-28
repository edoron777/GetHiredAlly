import { Settings } from 'lucide-react'

export function AdminSettings() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>Settings</h1>
      
      <div className="bg-white rounded-lg border p-8 text-center" style={{ borderColor: '#E5E7EB' }}>
        <Settings className="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Coming Soon</h2>
        <p className="text-gray-600">
          Admin settings and configuration options will be available here in a future update.
        </p>
      </div>
    </div>
  )
}
