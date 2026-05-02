import React from 'react';
import { Clarifier } from './components/Clarifier';
import { InputArea } from './components/InputArea';
import { IdeaCanvas } from './components/IdeaCanvas';
import styles from './styles/App.module.css';

function App() {
  return (
    <div className={styles.appContainer}>
      <header className={styles.header}>
        <div className={styles.logo}>SpecBuilderEngine</div>
        <div className={styles.version}>v0.1.0-alpha</div>
      </header>
      
      <main className={styles.main}>
        <div className={styles.leftPanel}>
          <Clarifier />
          <div className={styles.spacer} />
          <InputArea />
        </div>
        
        <div className={styles.rightPanel}>
          <IdeaCanvas />
        </div>
      </main>
    </div>
  );
}

export default App;
