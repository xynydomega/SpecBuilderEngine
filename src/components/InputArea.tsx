import { useState, useEffect } from 'react';
import { useSpecStore } from '../store/useSpecStore';
import styles from '../styles/InputArea.module.css';
import { Send } from 'lucide-react';

export const InputArea: React.FC = () => {
  const { currentStep, submitIntent, isComplete, reset, suggestions, isLoading } = useSpecStore();
  const [input, setInput] = useState('');

  useEffect(() => {
    setInput('');
  }, [currentStep]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    await submitIntent(input);
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
        {suggestions.map(chip => (
          <button 
            key={chip} 
            className={styles.chip}
            onClick={() => handleChipClick(chip)}
            disabled={isLoading}
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
          placeholder={isLoading ? "Processing..." : "Describe your intent..."}
          autoFocus
          disabled={isLoading}
        />
        <button type="submit" className={styles.sendButton} disabled={isLoading || !input.trim()}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};
