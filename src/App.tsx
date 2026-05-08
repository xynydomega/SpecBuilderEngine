import { useState, useEffect, useRef } from 'react'
import './App.css'
import InputArea from './components/InputArea'
import FeaturesPanel from './components/FeaturesPanel'
import AssistantPanel from './components/AssistantPanel'
import { Settings } from 'lucide-react'

interface Message {
  role: 'user' | 'agent';
  content: string;
}

function App() {
  const [chatHistory, setChatHistory] = useState<Message[]>([])
  const [patch, setPatch] = useState<Record<string, unknown> | null>(null)
  const [currentStage, setCurrentStage] = useState<string>('goal_definition')
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
        setCurrentStage(data.stage || 'unknown')
        if (data.patch && Object.keys(data.patch as object).length > 0) {
          setPatch(data.patch)
        }
      }
    } catch (err) {
      console.error("Failed to send message", err)
      setError("Agent is unresponsive. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleAcceptPatch = async (confirmedPatch: Record<string, unknown>) => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/agent/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patch: confirmedPatch })
      })
      const data = await res.json()
      setPatch(null)
      setCurrentStage(data.next_stage?.stage || 'unknown')
      // Next greeting comes from the Interrogator's next question in real flow,
      // but we can add a confirmation message.
    } catch (err) {
      console.error("Failed to apply changes", err)
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
        <Settings size={18} />
      </button>

      <FeaturesPanel 
        patch={patch} 
        onAccept={handleAcceptPatch} 
        onReject={handleRejectPatch}
        isLoading={isLoading}
      />

      <AssistantPanel currentStage={currentStage} />

      <main className="main-stage">
        {/* Path 1: App Branding */}
        <div className="app-branding">
          <h1>THE ARCHITECT</h1>
          <p className="subtitle">By XYNYD</p>
        </div>
        
        {/* Path 2 & 3: Content Area (Quote + Chat) */}
        <div className="content-area">
          <div className="chat-scroll">
            {chatHistory.map((msg, idx) => {
              // Path 2: First agent message as Stylized Hero Quote
              if (idx === 0 && msg.role === 'agent') {
                return (
                  <div key={idx} className="hero-quote-container">
                    <div className="quote-text">{msg.content}</div>
                  </div>
                )
              }
              
              // Path 3: Subsequent Chat Messages
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
        </div>

        {/* Path 4: Slim Floating Input Bar */}
        <div className="input-floating-container">
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>

        {error && <div className="error-banner">{error}</div>}
      </main>
    </div>
  )
}

export default App
