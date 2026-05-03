import { useState, useEffect } from 'react'
import './App.css'
import InputArea from './components/InputArea'
import BuilderSidebar from './components/BuilderSidebar'

function App() {
  const [patch, setPatch] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSchema()
  }, [])

  const fetchSchema = async () => {
    try {
      const res = await fetch('/api/schema')
      await res.json()
      // Schema state removed as it is currently unused in the UI
    } catch (err) {
      console.error("Failed to fetch schema", err)
      setError("Failed to connect to the Architect Engine.")
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
      <main className="main-content">
        <header className="app-header">
          <h1>THE ARCHITECT</h1>
          <p className="subtitle">By XYNYD</p>
        </header>
        
        <div className="center-stage">
          {error && <div className="error-banner">{error}</div>}
          <div className="welcome-text">
            <h2>System Outcome Definition</h2>
            <p>Describe your vision. The engine will decompose it into functional components.</p>
          </div>
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </main>

      <BuilderSidebar 
        patch={patch} 
        onAccept={handleAcceptPatch} 
        onReject={handleRejectPatch}
        isLoading={isLoading}
      />
    </div>
  )
}

export default App
