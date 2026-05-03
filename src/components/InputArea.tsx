import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  return (
    <div className="input-floating-bar">
      <div className="input-field-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What are we building today? Describe your feature..."
          disabled={isLoading}
          rows={1}
        />
        <button 
          onClick={() => handleSubmit()} 
          disabled={isLoading || !input.trim()} 
          className="send-btn-inside"
        >
          {isLoading ? <div className="spinner"></div> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
};

export default InputArea;
