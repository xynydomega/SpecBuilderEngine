import React from 'react';
import { useSpecStore } from '../store/useSpecStore';
import styles from '../styles/Clarifier.module.css';
import { Sparkles } from 'lucide-react';

export const Clarifier: React.FC = () => {
  const { spec, currentStep, isComplete } = useSpecStore();

  const getQuestion = () => {
    if (isComplete) return "Your specification is complete!";
    
    const goal = spec.goal || "your project";
    
    switch (currentStep) {
      case 'goal': return "What are you trying to build today?";
      case 'type': return `Is "${goal}" a screen, a feature, or a full system?`;
      case 'inputs': return `For ${goal}, what data does the user provide?`;
      case 'ui': return `How should the user interact with ${goal}?`;
      case 'actions': return "What should happen step-by-step when they interact?";
      case 'state': return "What are the key states (e.g., loading, success)?";
      case 'validation': return "What checks should be performed on the inputs?";
      case 'api': return "Does this need to talk to any external services?";
      case 'responses': return "How should the system respond to success or failure?";
      case 'outputs': return "What is the final result or data produced?";
      default: return "Thinking...";
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Sparkles size={20} className={styles.sparkle} />
        <span className={styles.status}>Intelligence Layer</span>
      </div>
      <h1 className={styles.question}>{getQuestion()}</h1>
      {!isComplete && (
        <p className={styles.subtext}>
          Current Focus: <strong>{currentStep}</strong>
        </p>
      )}
    </div>
  );
};
