import { useState, useEffect } from 'react'
// Triggering fresh build
import './App.css'
import InputArea from './components/InputArea'
import BuilderSidebar from './components/BuilderSidebar'

function App() {
  const [patch, setPatch] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [nextStep, setNextStep] = useState<any>(null)

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    setIsLoading(true)
    try {
      await fetchSchema()
      await fetchNextStep()
    } finally {
      setIsLoading(false)
    }
  }

  const fetchSchema = async () => {
    try {
      const res = await fetch('/api/schema')
      await res.json()
    } catch (err) {
      console.error("Failed to fetch schema", err)
      setError("Failed to connect to the Architect Engine.")
    }
  }

  const fetchNextStep = async () => {
    try {
      const res = await fetch('/api/sequencer/next')
      const data = await res.json()
      setNextStep(data)
    } catch (err) {
      console.error("Failed to fetch next step", err)
    }
  }

  const handleSendMessage = async (message: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/mapper/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: message })
      })
      const data = await res.json()
      if (data.error) {
        setError(data.error)
      } else {
        setPatch(data.patch)
      }
    } catch (err) {
      setError("Extraction failed. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleAcceptPatch = async (confirmedPatch: any) => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/mapper/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patch: confirmedPatch })
      })
      await res.json()
      setPatch(null)
      await fetchNextStep() // Get the next step after applying
    } catch (err) {
      setError("Failed to apply changes.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleRejectPatch = () => {
    setPatch(null)
  }

  return (
    <div className="app-container">
      <BuilderSidebar 
        patch={patch} 
        onAccept={handleAcceptPatch} 
        onReject={handleRejectPatch}
        isLoading={isLoading}
      />

      <main className="main-content">
        <header className="app-header">
          <h1>THE ARCHITECT</h1>
          <p className="subtitle">By XYNYD</p>
        </header>
        
        <div className="center-stage">
          {error && <div className="error-banner">{error}</div>}
          <div className="welcome-text">
            <h2>{nextStep?.prompt || "System Outcome Definition"}</h2>
            <p className="node-indicator">Target: {nextStep?.node || "Goal"}</p>
          </div>
        </div>

        <div className="bottom-right-container">
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </main>
    </div>
  )
}

export default App
