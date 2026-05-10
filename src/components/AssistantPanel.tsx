import { useState } from 'react'
import { X, Send, Sparkles, HelpCircle, MessageSquare } from 'lucide-react'
import './AssistantPanel.css'

interface AssistantPanelProps {
  response: any | null;
  dialogueState: any | null;
}

function AssistantPanel({ response, dialogueState }: AssistantPanelProps) {
  const [isOpen, setIsOpen] = useState(false)
  const toggleOpen = () => setIsOpen(!isOpen)

  return (
    <div className={`assistant-floating-container ${isOpen ? 'open' : 'closed'}`}>
      {!isOpen && (
        <button className="assistant-trigger" onClick={toggleOpen}>
          <Sparkles size={20} />
          <span>Active Layer: {response?.type === "ASSISTANT_MESSAGE" ? "Assistant" : "Interrogator"}</span>
        </button>
      )}

      {isOpen && (
        <div className="assistant-window">
          <div className="assistant-header">
            <div className="header-title">
              {response?.type === "ASSISTANT_MESSAGE" ? <HelpCircle size={16} /> : <MessageSquare size={16} />}
              <span>{response?.type === "ASSISTANT_MESSAGE" ? "Semantic Assistant" : "Structural Interrogator"}</span>
            </div>
            <button className="close-btn" onClick={toggleOpen}><X size={16} /></button>
          </div>
          
          <div className="assistant-content">
            <div className="dialogue-status">
              <div className="status-item">
                <strong>Focus:</strong> {dialogueState?.active_focus_node || "None"}
              </div>
              <div className="status-item">
                <strong>Ambiguity:</strong> {(dialogueState?.ambiguity_level * 100).toFixed(0)}%
              </div>
            </div>

            {response?.type === "INTERROGATOR_MESSAGE" && (
              <div className="interrogator-layer">
                <h4>Interrogation Focus</h4>
                <p><strong>Goal:</strong> {response.expected_resolution}</p>
                {response.optional_suggestion && (
                  <div className="suggestion">
                    <strong>Suggestion:</strong> {response.optional_suggestion}
                  </div>
                )}
              </div>
            )}

            {response?.type === "ASSISTANT_MESSAGE" && (
              <div className="assistant-layer">
                <h4>Stabilization Insight</h4>
                <p className="concept">Concept: {response.concept}</p>
                <p className="explanation">{response.explanation}</p>
                
                {response.alternatives?.length > 0 && (
                  <div className="alternatives">
                    <h5>Alternatives</h5>
                    {response.alternatives.map((alt: any, i: number) => (
                      <div key={i} className="alt-item">
                        <strong>{alt.option}:</strong> {alt.impact}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {!response && (
              <div className="welcome-msg">
                Initializing Cognition Runtime... Define your core intent.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AssistantPanel
