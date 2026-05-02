import React, { useState, useEffect } from 'react';
import { useSpecStore } from '../store/useSpecStore';
import styles from '../styles/InputArea.module.css';
import { Send } from 'lucide-react';

export const InputArea: React.FC = () => {
  const { currentStep, updateField, isComplete, reset } = useSpecStore();
  const [input, setInput] = useState('');

  useEffect(() => {
    setInput('');
  }, [currentStep]);

  const getSuggestions = () => {
    switch (currentStep) {
      case 'type': return ['Screen', 'Feature', 'System', 'API'];
      case 'inputs': return ['Email', 'Password', 'Username', 'Title'];
      case 'ui': return ['Form', 'Button', 'Modal', 'List'];
      case 'state': return ['Idle', 'Loading', 'Success', 'Error'];
      default: return [];
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    // Mock Semantic Mapper: Just split by comma for now
    if (currentStep === 'goal') {
      updateField(currentStep, input);
    } else if (currentStep === 'responses') {
       updateField(currentStep, { success: input });
    } else {
      updateField(currentStep, input.split(',').map(i => i.trim()));
    }
    
    setInput('');
  };

  const handleChipClick = (value: string) => {
    const newVal = input ? `${input}, ${value}` : value;
    setInput(newVal);
  };

  if (isComplete) {
    return (
      <div className={styles.container}>
        <button className={styles.resetButton} onClick={reset}>
          Build Another Spec
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.chips}>
        {getSuggestions().map(chip => (
          <button 
            key={chip} 
            className={styles.chip}
            onClick={() => handleChipClick(chip)}
          >
            {chip}
          </button>
        ))}
      </div>
      <form className={styles.inputForm} onSubmit={handleSubmit}>
        <input 
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your intent..."
          autoFocus
        />
        <button type="submit" className={styles.sendButton}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};
