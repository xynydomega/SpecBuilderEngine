import React from 'react';
import { Check, X, Info } from 'lucide-react';

interface BuilderSidebarProps {
  patch: any;
  onAccept: (patch: any) => void;
  onReject: () => void;
  isLoading: boolean;
}

const BuilderSidebar: React.FC<BuilderSidebarProps> = ({ patch, onAccept, onReject, isLoading }) => {
  if (!patch && !isLoading) {
    return (
      <div className="sidebar-empty">
        <p>Your blueprint will appear here as you describe your project.</p>
      </div>
    );
  }

  const renderComponent = (key: string, data: any) => {
    if (!data) return null;

    let content = null;
    if (key === 'goal') {
      content = <p className="component-value">"{data.state.value}"</p>;
    } else if (key === 'type_hypothesis') {
      content = (
        <ul className="component-list">
          {data.state.components.map((c: any, i: number) => (
            <li key={i} title={c.reason}>
              {c.name}
            </li>
          ))}
        </ul>
      );
    } else if (key === 'inputs') {
      content = (
        <ul className="component-list">
          {Object.entries(data.state.fields).map(([field, details]: [string, any], i: number) => (
            <li key={i} title={details.reason}>
              {field}
            </li>
          ))}
        </ul>
      );
    }

    return (
      <div key={key} className="sidebar-node">
        <div className="node-header">
          <span className="node-title">{key.toUpperCase()}</span>
          <span className="node-confidence">{(data.meta.confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="node-reason">
          <Info size={12} /> {data.target.role}
        </div>
        <div className="node-content">{content}</div>
      </div>
    );
  };

  return (
    <div className="builder-sidebar">
      <div className="sidebar-header">
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

      <div className="sidebar-body">
        {isLoading ? (
          <div className="sidebar-loading">
            <div className="spinner large"></div>
            <p>Analyzing architecture...</p>
          </div>
        ) : (
          Object.entries(patch || {}).map(([key, data]) => renderComponent(key, data))
        )}
      </div>
    </div>
  );
};

export default BuilderSidebar;
