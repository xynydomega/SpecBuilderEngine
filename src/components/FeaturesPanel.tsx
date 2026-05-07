import React from 'react';
import { Check, X, Info, Layers, Tool, Component, Target, Shield, Activity } from 'lucide-react';

interface FeaturesPanelProps {
  patch: any;
  onAccept: (patch: any) => void;
  onReject: () => void;
  isLoading: boolean;
}

const TreeNode = ({ id, node }: { id: string, node: any }) => {
  const data = node.data || {};
  const meta = node.meta || {};
  const semantic = data.semantic_layer || {};
  const intent = semantic.intent?.data || {};
  const constraints = semantic.constraints?.data || {};
  const state = data.state_system?.config?.data || {};

  const getIcon = (type: string) => {
    switch (type) {
      case 'feature': return <Layers size={14} className="icon-feature" />;
      case 'component': return <Component size={14} className="icon-component" />;
      case 'tool': return <Tool size={14} className="icon-tool" />;
      default: return <Target size={14} className="icon-goal" />;
    }
  };

  return (
    <div className={`tree-node ${node.type}`}>
      <div className="node-main">
        <div className="node-header">
          <div className="title-area">
            {getIcon(node.type)}
            <span className="node-name">{data.name || id}</span>
          </div>
          <div className="meta-area">
            <span className="node-confidence">{(meta.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="node-details">
          {intent.target && (
            <div className="detail-item">
              <Activity size={10} />
              <span><strong>Intent:</strong> {intent.target} ({intent.direction})</span>
            </div>
          )}
          {(constraints.global_rules?.length > 0 || constraints.inheritance_rules?.length > 0) && (
            <div className="detail-item">
              <Shield size={10} />
              <span><strong>Rules:</strong> {constraints.global_rules?.length || 0} active</span>
            </div>
          )}
        </div>
      </div>

      {node.children && Object.keys(node.children).length > 0 && (
        <div className="node-children">
          {Object.entries(node.children).map(([cid, cnode]: [string, any]) => (
            <TreeNode key={cid} id={cid} node={cnode} />
          ))}
        </div>
      )}
    </div>
  );
};

const FeaturesPanel: React.FC<FeaturesPanelProps> = ({ patch, onAccept, onReject, isLoading }) => {
  // If patch is present, we wrap it in a root if it doesn't have the "config" key
  const rootNode = patch?.config ? patch.config : (patch ? { type: 'goal', data: { name: "Proposed Change" }, children: patch } : null);

  return (
    <div className="features-panel">
      <div className="panel-header">
        <h2>Blueprint</h2>
        {patch && (
          <div className="patch-actions">
            <button onClick={() => onAccept(patch)} className="accept-button" title="Accept all">
              <Check size={18} />
            </button>
            <button onClick={onReject} className="reject-button" title="Reject all">
              <X size={18} />
            </button>
          </div>
        )}
      </div>

      <div className="panel-body">
        {isLoading ? (
          <div className="sidebar-loading">
            <div className="spinner large"></div>
            <p>Architecting...</p>
          </div>
        ) : !rootNode ? (
          <div className="sidebar-empty">
            <p>The Architect is waiting for your vision.</p>
          </div>
        ) : (
          <div className="tree-container">
            <TreeNode id="root" node={rootNode} />
          </div>
        )}
      </div>
    </div>
  );
};

export default FeaturesPanel;
