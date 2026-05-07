import { useState } from 'react'
import { X, Send, Sparkles } from 'lucide-react'
import './AssistantPanel.css'

interface AssistantPanelProps {
  currentStage: string;
}

function AssistantPanel({ currentStage }: AssistantPanelProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', content: string}[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const toggleOpen = () => setIsOpen(!isOpen)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const userMsg = input
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch('/api/agent/assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: userMsg })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now." }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`assistant-floating-container ${isOpen ? 'open' : 'closed'}`}>
      {!isOpen && (
        <button className="assistant-trigger" onClick={toggleOpen}>
          <Sparkles size={20} />
          <span>Ask Assistant</span>
        </button>
      )}

      {isOpen && (
        <div className="assistant-window">
          <div className="assistant-header">
            <div className="header-title">
              <Sparkles size={16} />
              <span>Executive Assistant</span>
            </div>
            <button className="close-btn" onClick={toggleOpen}><X size={16} /></button>
          </div>
          
          <div className="assistant-content">
            <div className="stage-badge">Stage: {currentStage.replace('_', ' ')}</div>
            {messages.length === 0 && (
              <div className="welcome-msg">
                I'm your Guardian Angel. Stuck? Not sure why the Interrogator is asking for something? Just ask me.
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`msg-bubble ${m.role}`}>
                {m.content}
              </div>
            ))}
            {isLoading && <div className="msg-bubble assistant loading">...</div>}
          </div>

          <div className="assistant-input-area">
            <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
              placeholder="How can I help?"
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend}><Send size={16} /></button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AssistantPanel
