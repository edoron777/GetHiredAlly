import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

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
  const [isHovered, setIsHovered] = useState(false)

  const handleClick = () => {
    if (isActive && navigateTo) {
      navigate(navigateTo)
    }
  }

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        width: '280px',
        minHeight: '280px',
        backgroundColor: 'white',
        border: '1px solid #E5E7EB',
        borderRadius: '12px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        textAlign: 'center',
        transition: 'all 0.2s ease-in-out',
        cursor: isActive ? 'pointer' : 'not-allowed',
        opacity: isActive ? 1 : 0.6,
        boxShadow: isActive && isHovered 
          ? '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
          : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        transform: isActive && isHovered ? 'translateY(-2px)' : 'translateY(0)'
      }}
    >
      <div style={{ fontSize: '32px', marginBottom: '12px' }}>{icon}</div>
      <h3 style={{ 
        fontSize: '18px', 
        fontWeight: 600, 
        marginBottom: '4px', 
        color: '#1E3A5F' 
      }}>
        {title}
      </h3>
      <p style={{ 
        fontSize: '14px', 
        marginBottom: '8px', 
        color: '#6B7280' 
      }}>
        {subtitle}
      </p>
      {description && (
        <p style={{ 
          fontSize: '14px', 
          color: '#374151' 
        }}>
          {description}
        </p>
      )}
      <div style={{ flexGrow: 1 }} />
      <button
        disabled={!isActive}
        style={{
          marginTop: 'auto',
          padding: '10px 20px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 500,
          border: 'none',
          cursor: isActive ? 'pointer' : 'not-allowed',
          backgroundColor: isActive ? '#1E3A5F' : '#E5E7EB',
          color: isActive ? 'white' : '#9CA3AF',
          transition: 'background-color 0.2s'
        }}
        onMouseEnter={(e) => {
          if (isActive) {
            e.currentTarget.style.backgroundColor = '#162d4a'
          }
        }}
        onMouseLeave={(e) => {
          if (isActive) {
            e.currentTarget.style.backgroundColor = '#1E3A5F'
          }
        }}
      >
        {buttonText}
      </button>
    </div>
  )
}
