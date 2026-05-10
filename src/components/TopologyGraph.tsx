import React from 'react';
import { Layers, Activity, Target, Eye, EyeOff, Zap, Share2 } from 'lucide-react';

interface TopologyGraphProps {
  shadowGraph: any | null;
  confirmedTree: any | null;
  isLoading: boolean;
}

const ShadowNode = ({ node }: any) => {
  const getIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'FEATURE': return <Layers size={14} className="icon-feature" />;
      case 'DATA_MODEL': return <Activity size={14} className="icon-component" />;
      case 'GOAL': return <Target size={14} className="icon-goal" />;
      default: return <Zap size={14} className="icon-tool" />;
    }
  };

  const statusClass = node.status.toLowerCase();
  
  return (
    <div className={`topology-node ghost-node ${statusClass}`}>
      <div className="node-content">
        <div className="node-header">
          {getIcon(node.type)}
          <span className="node-label">{node.hypothesis?.name || node.id}</span>
          <EyeOff size={12} className="status-icon" />
        </div>
        <div className="node-meta">
          <span className="confidence-pill">{(node.total_confidence * 100).toFixed(0)}%</span>
          <span className="status-pill">{node.status}</span>
        </div>
      </div>
    </div>
  );
};

const HardNode = ({ node }: any) => {
  return (
    <div className="topology-node hard-node">
      <div className="node-content">
        <div className="node-header">
          <Target size={14} className="icon-goal" />
          <span className="node-label">{node.name || "Confirmed Node"}</span>
          <Eye size={12} className="status-icon" />
        </div>
      </div>
    </div>
  );
};

const TopologyGraph: React.FC<TopologyGraphProps> = ({ shadowGraph, confirmedTree, isLoading }) => {
  return (
    <div className="topology-graph">
      <div className="panel-header">
        <h2>Relational Substrate</h2>
        <div className="runtime-badge">v1.3.0</div>
      </div>

      <div className="panel-body">
        {isLoading ? (
          <div className="topology-loading">
            <div className="pulse-circle"></div>
            <p>Evolving topology...</p>
          </div>
        ) : (
          <div className="graph-layers">
            <div className="graph-section hard-layer">
              <h3>Runtime (Confirmed)</h3>
              {confirmedTree?.nodes?.map((n: any, i: number) => (
                <HardNode key={i} node={n} />
              ))}
              {(!confirmedTree?.nodes || confirmedTree.nodes.length === 0) && (
                <p className="empty-msg">No stabilized nodes projected.</p>
              )}
            </div>

            <div className="graph-section shadow-layer">
              <h3>Shadow Graph (Probabilistic)</h3>
              <div className="substrate-stats">
                <div className="stat-item">
                  <Share2 size={12} />
                  <span>Edges: {shadowGraph?.edges?.length || 0}</span>
                </div>
                <div className="stat-item">
                  <Activity size={12} />
                  <span>Convergence: {(shadowGraph?.convergence_score * 100 || 0).toFixed(0)}%</span>
                </div>
              </div>
              
              <div className="node-grid">
                {shadowGraph?.nodes?.map((n: any) => (
                  <ShadowNode key={n.id} node={n} />
                ))}
              </div>

              {shadowGraph?.active_frontier?.length > 0 && (
                <div className="active-frontier">
                  <h4>Active Frontier</h4>
                  <div className="frontier-tags">
                    {shadowGraph.active_frontier.map((id: string, i: number) => (
                      <span key={i} className="frontier-tag">{id}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TopologyGraph;
