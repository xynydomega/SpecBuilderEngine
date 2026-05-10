import { useState, useEffect, useRef } from 'react'
import './App.css'
import InputArea from './components/InputArea'
import TopologyGraph from './components/TopologyGraph'
import AssistantPanel from './components/AssistantPanel'
import { Settings } from 'lucide-react'

interface Message {
  role: 'user' | 'agent';
  content: string;
}

function App() {
  const [chatHistory, setChatHistory] = useState<Message[]>([])
  const [runtimeState, setRuntimeState] = useState<any | null>(null)
  const [currentResponse, setCurrentResponse] = useState<any | null>(null)
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
      const res = await fetch('/api/cognition/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: message })
      })
      const data = await res.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        const response = data.response;
        setRuntimeState(data.state);
        setCurrentResponse(response);
        
        let agentText = "";
        if (response.type === "INTERROGATOR_MESSAGE") {
          agentText = response.question;
        } else {
          agentText = response.explanation;
        }
        
        setChatHistory(prev => [...prev, { role: 'agent', content: agentText }])
      }
    } catch (err) {
      console.error("Failed to send message", err)
      setError("Agent is unresponsive. Please check your connection.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`app-container sidebar-${sidebarSide}`}>
      <button className="settings-btn" onClick={toggleSidebarSide} title="Move Topology Panel">
        <Settings size={18} />
      </button>

      <TopologyGraph 
        shadowGraph={runtimeState?.shadow_graph}
        confirmedTree={runtimeState?.confirmed_tree}
        isLoading={isLoading}
      />

      <AssistantPanel 
        response={currentResponse}
        dialogueState={runtimeState?.dialogue_state}
      />

      <main className="main-stage">
        <div className="app-branding">
          <h1>COGNITION RUNTIME</h1>
          <p className="subtitle">SpecBuilderCognitionRuntime v1.3.0</p>
        </div>
        
        <div className="content-area">
          <div className="chat-scroll">
            {chatHistory.map((msg, idx) => {
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
        </div>

        <div className="input-floating-container">
          <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>

        {error && <div className="error-banner">{error}</div>}
      </main>
    </div>
  )
}

export default App
