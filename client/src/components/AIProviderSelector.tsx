import { Sparkles, Zap } from 'lucide-react'

export type Provider = 'claude' | 'gemini'

interface AIProviderSelectorProps {
  selectedProvider: Provider
  onProviderChange: (provider: Provider) => void
  service?: 'xray' | 'smart_questions'
}

interface ProviderInfo {
  id: Provider
  name: string
  icon: React.ReactNode
  description: string
  estimatedCost: string
  speed: string
  color: string
  bgColor: string
  borderColor: string
}

const providers: ProviderInfo[] = [
  {
    id: 'claude',
    name: 'Claude',
    icon: <Sparkles className="h-5 w-5" />,
    description: 'Best for detailed analysis',
    estimatedCost: '~$0.02',
    speed: 'Moderate',
    color: '#D97706',
    bgColor: '#FEF3C7',
    borderColor: '#F59E0B'
  },
  {
    id: 'gemini',
    name: 'Gemini',
    icon: <Zap className="h-5 w-5" />,
    description: 'Fast and cost-effective',
    estimatedCost: '~$0.01',
    speed: 'Fast',
    color: '#059669',
    bgColor: '#D1FAE5',
    borderColor: '#10B981'
  }
]

export function AIProviderSelector({ selectedProvider, onProviderChange, service }: AIProviderSelectorProps) {
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium" style={{ color: '#1E3A5F' }}>AI Provider</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">Optional</span>
      </div>
      <div className="flex gap-3">
        {providers.map((provider) => {
          const isSelected = selectedProvider === provider.id
          return (
            <button
              key={provider.id}
              type="button"
              onClick={() => onProviderChange(provider.id)}
              className="flex-1 p-3 rounded-lg border-2 transition-all text-left"
              style={{
                borderColor: isSelected ? provider.borderColor : '#E5E7EB',
                backgroundColor: isSelected ? provider.bgColor : 'white',
                cursor: 'pointer'
              }}
            >
              <div className="flex items-center gap-2 mb-1">
                <span style={{ color: provider.color }}>{provider.icon}</span>
                <span className="font-medium" style={{ color: isSelected ? provider.color : '#374151' }}>
                  {provider.name}
                </span>
                {isSelected && (
                  <span 
                    className="ml-auto text-xs px-1.5 py-0.5 rounded"
                    style={{ backgroundColor: provider.color, color: 'white' }}
                  >
                    Selected
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 mb-1">{provider.description}</p>
              <div className="flex items-center gap-3 text-xs">
                <span style={{ color: provider.color }}>
                  Est: {provider.estimatedCost}
                </span>
                <span className="text-gray-400">|</span>
                <span className="text-gray-500">{provider.speed}</span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
