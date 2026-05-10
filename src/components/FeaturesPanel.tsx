import React from 'react';
import { Check, X, Layers, Wrench, Component, Target, Shield, Activity, Eye, EyeOff } from 'lucide-react';

interface FeaturesPanelProps {
  shadowTree: any | null;
  confirmedTree: any | null;
  onConfirmHypothesis: (id: string) => void;
  isLoading: boolean;
}

const TreeNode = ({ id, name, type, confidence, isShadow, onConfirm }: any) => {
  const getIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'FEATURE': return <Layers size={14} className="icon-feature" />;
      case 'COMPONENT': return <Component size={14} className="icon-component" />;
      case 'TOOL': return <Wrench size={14} className="icon-tool" />;
      default: return <Target size={14} className="icon-goal" />;
    }
  };

  return (
    <div className={`tree-node ${type.toLowerCase()} ${isShadow ? 'shadow-path' : 'confirmed-path'}`}>
      <div className="node-main">
        <div className="node-header">
          <div className="title-area">
            {getIcon(type)}
            <span className="node-name">{name || id}</span>
            {isShadow ? <EyeOff size={12} className="shadow-icon" /> : <Eye size={12} className="confirmed-icon" />}
          </div>
          {confidence !== undefined && (
            <div className="meta-area">
              <span className="node-confidence">{(confidence * 100).toFixed(0)}%</span>
              {isShadow && onConfirm && (
                <button onClick={() => onConfirm(id)} className="confirm-btn">
                  <Check size={12} />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const FeaturesPanel: React.FC<FeaturesPanelProps> = ({ shadowTree, confirmedTree, onConfirmHypothesis, isLoading }) => {
  return (
    <div className="features-panel">
      <div className="panel-header">
        <h2>Cognition Runtime</h2>
        <div className="runtime-badge">v1.0.0</div>
      </div>

      <div className="panel-body">
        {isLoading ? (
          <div className="sidebar-loading">
            <div className="spinner large"></div>
            <p>Inferring structure...</p>
          </div>
        ) : (
          <div className="tree-container">
            {/* Confirmed Section */}
            <div className="tree-section confirmed">
              <h4>Confirmed Tree</h4>
              {!confirmedTree?.goal && !confirmedTree?.features.length && (
                <p className="empty-msg">No confirmed structure yet.</p>
              )}
              {confirmedTree?.goal && (
                <TreeNode name={confirmedTree.goal.name} type="GOAL" isShadow={false} />
              )}
              {confirmedTree?.features?.map((f: any, i: number) => (
                <TreeNode key={i} name={f.name} type="FEATURE" isShadow={false} />
              ))}
            </div>

            {/* Shadow Section */}
            <div className="tree-section shadow">
              <h4>Shadow Tree (Latent)</h4>
              {shadowTree?.goal_hypotheses?.map((h: any) => (
                <TreeNode 
                  key={h.id} 
                  id={h.id}
                  name={h.content.target} 
                  type="GOAL" 
                  confidence={h.confidence}
                  isShadow={true}
                  onConfirm={onConfirmHypothesis}
                />
              ))}
              {shadowTree?.feature_hypotheses?.map((h: any) => (
                <TreeNode 
                  key={h.id} 
                  id={h.id}
                  name={h.content.name} 
                  type="FEATURE" 
                  confidence={h.confidence}
                  isShadow={true}
                  onConfirm={onConfirmHypothesis}
                />
              ))}
              
              {shadowTree?.assumptions?.length > 0 && (
                <div className="assumptions-list">
                  <h5>Assumptions</h5>
                  <ul>
                    {shadowTree.assumptions.map((a: string, i: number) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeaturesPanel;
