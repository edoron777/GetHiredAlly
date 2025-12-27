import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ServiceCard } from './ServiceCard'
import { getUser, isAuthenticated } from '@/lib/auth'

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

  const services = [
    {
      icon: '🔍',
      title: 'Decode Any Job Description',
      subtitle: 'Turn job description into interview-winning insights',
      description: '',
      buttonText: 'Get Started',
      isActive: true,
      navigateTo: '/service/understand-job'
    },
    {
      icon: '❓',
      title: 'Prepare for Questions',
      subtitle: 'Questions Predictor',
      description: 'What will they ask me?',
      buttonText: 'Get Started',
      isActive: true,
      navigateTo: '/service/predict-questions'
    },
    {
      icon: '💬',
      title: 'Craft Your Answers',
      subtitle: 'My Interview Playbook',
      description: 'What should I say?',
      buttonText: 'Coming Soon',
      isActive: false
    },
    {
      icon: '📄',
      title: 'Optimize Your CV',
      subtitle: 'CV Scanner',
      description: "What's wrong with my CV?",
      buttonText: 'Get Started',
      isActive: true,
      navigateTo: '/service/cv-optimizer',
      videoUrl: 'https://www.youtube.com/embed/Tt08KmFfIYQ',
      videoTitle: 'How CV Optimizer Works'
    }
  ]

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            Welcome back{firstName ? `, ${firstName}` : ''}!
          </h1>
          <p className="text-lg" style={{ color: '#374151' }}>
            What would you like to work on today?
          </p>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '24px', alignItems: 'stretch' }}>
          {services.map((service, index) => (
            <ServiceCard
              key={index}
              icon={service.icon}
              title={service.title}
              subtitle={service.subtitle}
              description={service.description}
              buttonText={service.buttonText}
              isActive={service.isActive}
              navigateTo={service.navigateTo}
              videoUrl={service.videoUrl}
              videoTitle={service.videoTitle}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
