import { useSpecStore } from '../store/useSpecStore';
import styles from '../styles/Clarifier.module.css';
import { Sparkles } from 'lucide-react';

export const Clarifier: React.FC = () => {
  const { currentStep, isComplete, currentQuestion } = useSpecStore();

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Sparkles size={20} className={styles.sparkle} />
        <span className={styles.status}>Intelligence Layer</span>
      </div>
      <h1 className={styles.question}>{currentQuestion}</h1>
      {!isComplete && (
        <p className={styles.subtext}>
          Current Focus: <strong>{currentStep}</strong>
        </p>
      )}
    </div>
  );
};
