import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUser, isAuthenticated } from '@/lib/auth'
import { SECTION_A, SECTION_B } from '../config/homePageServices'
import { HomeSection } from './home/HomeSection'
import { SectionSeparator } from './common'

export function Dashboard() {
  const navigate = useNavigate()
  const [firstName, setFirstName] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const user = getUser()
    if (user?.name) {
      const first = user.name.split(' ')[0]
      setFirstName(first)
    }
  }, [navigate])

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            Welcome back{firstName ? `, ${firstName}` : ''}!
          </h1>
          <p className="text-lg" style={{ color: '#374151' }}>
            What would you like to work on today?
          </p>
        </div>

        <HomeSection section={SECTION_A} />

        <SectionSeparator />

        <HomeSection section={SECTION_B} />
      </div>
    </div>
  )
}
