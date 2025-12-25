import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

export function LandingPage() {
  const [healthStatus, setHealthStatus] = useState<string>('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealthStatus(data.status))
      .catch(() => setHealthStatus('error'))
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center space-y-8">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Welcome to Your App
        </h1>
        <p className="text-lg text-[hsl(var(--muted-foreground))]">
          Built with React, Vite, Tailwind CSS, shadcn/ui, and FastAPI
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg">Get Started</Button>
          <Button variant="outline" size="lg">Learn More</Button>
        </div>
        <div className="mt-8 p-4 rounded-lg bg-[hsl(var(--secondary))]">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            API Health Status: <span className="font-semibold text-[hsl(var(--foreground))]">{healthStatus}</span>
          </p>
        </div>
      </div>
    </div>
  )
}
