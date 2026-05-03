import { useState, useEffect, useRef } from 'react'
import './App.css'
import InputArea from './components/InputArea'
import BuilderSidebar from './components/BuilderSidebar'

interface Message {
  role: 'user' | 'agent';
  content: string;
}

function App() {
  const [chatHistory, setChatHistory] = useState<Message[]>([])
  const [patch, setPatch] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    initAgent()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const initAgent = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/agent/init')
      const data = await res.json()
      setChatHistory([{ role: 'agent', content: data.message }])
    } catch (err) {
      console.error("Failed to init agent", err)
      setError("Failed to connect to the Architect Engine.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async (message: string) => {
    const newUserMessage: Message = { role: 'user', content: message }
    setChatHistory(prev => [...prev, newUserMessage])
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/agent/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: message })
      })
      const data = await res.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setChatHistory(prev => [...prev, { role: 'agent', content: data.message }])
        if (data.patch && Object.keys(data.patch).length > 0) {
          setPatch(data.patch)
        }
      }
    } catch (err) {
      setError("Agent is unresponsive. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleAcceptPatch = async (confirmedPatch: any) => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/agent/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patch: confirmedPatch })
      })
      const data = await res.json()
      setPatch(null)
      setChatHistory(prev => [...prev, { role: 'agent', content: data.next_step_prompt }])
    } catch (err) {
      setError("Failed to apply changes.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleRejectPatch = () => {
    setPatch(null)
    setChatHistory(prev => [...prev, { role: 'agent', content: "I understand. Let's try to redefine that part. What would you like to change?" }])
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
        
        <div className="chat-container">
          <div className="chat-history">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`message-wrapper ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-wrapper agent">
                <div className="message-bubble loading">
                  <div className="typing-dots">
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="input-container-floating">
            <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
