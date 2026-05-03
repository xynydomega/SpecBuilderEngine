import { useState, useEffect, useRef } from 'react'
import './App.css'
import InputArea from './components/InputArea'
import FeaturesPanel from './components/FeaturesPanel'
import { Settings } from 'lucide-react'

interface Message {
  role: 'user' | 'agent';
  content: string;
}

function App() {
  const [chatHistory, setChatHistory] = useState<Message[]>([])
  const [patch, setPatch] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sidebarSide, setSidebarSide] = useState<'left' | 'right'>('left')
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

  const toggleSidebarSide = () => {
    setSidebarSide(prev => prev === 'left' ? 'right' : 'left')
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
    <div className={`app-container sidebar-${sidebarSide}`}>
      <button className="settings-btn" onClick={toggleSidebarSide} title="Move Features Panel">
        <Settings size={20} />
      </button>

      <FeaturesPanel 
        patch={patch} 
        onAccept={handleAcceptPatch} 
        onReject={handleRejectPatch}
        isLoading={isLoading}
      />

      <main className="main-stage">
        <div className="app-branding">
          <h1>THE ARCHITECT</h1>
          <p className="subtitle">By XYNYD</p>
        </div>
        
        <div className="content-area">
          <div className="chat-scroll">
            {chatHistory.map((msg, idx) => {
              // First agent message is treated as the stylized hero quote
              if (idx === 0 && msg.role === 'agent') {
                return (
                  <div key={idx} className="hero-quote-container">
                    <div className="quote-text">{msg.content}</div>
                  </div>
                )
              }
              
              return (
                <div key={idx} className={`message-wrapper ${msg.role}`}>
                  <div className="message-card">
                    {msg.content}
                  </div>
                </div>
              )
            })}
            
            {isLoading && (
              <div className="message-wrapper agent">
                <div className="message-card loading">
                  <div className="typing-dots">
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      </main>
    </div>
  )
}

export default App
