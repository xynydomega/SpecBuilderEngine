import { useSpecStore } from '../store/useSpecStore';
import type { SpecNode } from '../types/spec';
import { NODE_LABELS } from '../types/spec';
import styles from '../styles/IdeaCanvas.module.css';
import { CheckCircle2, Circle } from 'lucide-react';

export const IdeaCanvas: React.FC = () => {
  const { spec, currentStep } = useSpecStore();

  const renderNode = (node: SpecNode) => {
    let content: any = null;
    if (node === 'goal') content = spec.goal;
    else if (node === 'type') content = spec.type_hypothesis.join(', ');
    else if (node === 'inputs') content = spec.inputs.join(', ');
    else if (node === 'ui') content = spec.ui.join(', ');
    else if (node === 'actions') content = spec.behavior.actions.join(', ');
    else if (node === 'state') content = spec.state.join(', ');
    else if (node === 'validation') content = spec.behavior.validation.join(', ');
    else if (node === 'api') content = spec.behavior.api_calls.join(', ');
    else if (node === 'responses') content = Object.keys(spec.behavior.responses).length > 0 ? 'Defined' : null;
    else if (node === 'outputs') content = spec.outputs.join(', ');

    const isPopulated = !!content;
    const isActive = currentStep === node;

    return (
      <div 
        key={node} 
        className={`${styles.node} ${isPopulated ? styles.populated : ''} ${isActive ? styles.active : ''} ${isPopulated ? 'animate-shimmer' : ''}`}
      >
        <div className={styles.nodeHeader}>
          {isPopulated ? <CheckCircle2 size={16} className={styles.iconDone} /> : <Circle size={16} className={styles.iconTodo} />}
          <span className={styles.nodeLabel}>{NODE_LABELS[node]}</span>
        </div>
        {content && <div className={styles.nodeContent}>{content}</div>}
      </div>
    );
  };

  return (
    <div className={styles.canvasContainer}>
      <h2 className={styles.title}>Evolutionary Spec</h2>
      <div className={styles.grid}>
        {(Object.keys(NODE_LABELS) as SpecNode[]).map(renderNode)}
      </div>
    </div>
  );
};
