import { useNavigate } from 'react-router-dom'

interface ServiceCardProps {
  icon: string
  title: string
  subtitle: string
  description: string
  buttonText: string
  isActive: boolean
  navigateTo?: string
}

export function ServiceCard({
  icon,
  title,
  subtitle,
  description,
  buttonText,
  isActive,
  navigateTo
}: ServiceCardProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (isActive && navigateTo) {
      navigate(navigateTo)
    }
  }

  return (
    <div
      onClick={handleClick}
      className={`
        w-[280px] h-[250px] bg-white border border-[#E5E7EB] rounded-lg text-center
        transition-all duration-200 ease-in-out flex flex-col
        ${isActive 
          ? 'cursor-pointer hover:shadow-lg hover:-translate-y-0.5' 
          : 'opacity-60 cursor-not-allowed'
        }
      `}
      style={{ padding: '24px' }}
    >
      <div className="text-[32px] mb-3">{icon}</div>
      <h3 className="text-lg font-semibold mb-1" style={{ color: '#1E3A5F' }}>
        {title}
      </h3>
      <p className="text-xs italic mb-2" style={{ color: '#6B7280' }}>
        {subtitle}
      </p>
      {description && (
        <p className="text-sm" style={{ color: '#374151' }}>
          {description}
        </p>
      )}
      <div className="flex-grow" />
      <button
        disabled={!isActive}
        className={`
          px-5 py-2.5 rounded-md text-sm font-medium transition-colors
          ${isActive 
            ? 'bg-[#1E3A5F] text-white hover:bg-[#162d4a]' 
            : 'bg-[#E5E7EB] text-[#9CA3AF] cursor-not-allowed'
          }
        `}
      >
        {buttonText}
      </button>
    </div>
  )
}
