import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

const NODE_COLORS = {
  PERSON:       "#6366f1",
  VEHICLE:      "#f59e0b",
  LOCATION:     "#10b981",
  PHONE:        "#3b82f6",
  CASE:         "#ef4444",
  ORGANIZATION: "#8b5cf6",
  UNKNOWN:      "#94a3b8",
};

const EDGE_COLORS = {
  CALLED:           "#60a5fa",
  TRANSFERRED_MONEY:"#34d399",
  MET:              "#a78bfa",
  VISITED:          "#10b981",
  USED_VEHICLE:     "#f59e0b",
  INVOLVED_IN:      "#f87171",
  USES_PHONE:       "#38bdf8",
  ASSOCIATED_WITH:  "#94a3b8",
};

export default function NetworkGraph({ nodes, edges, onNodeClick }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !nodes?.length) return;

    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: {
        nodes: nodes.map((n) => ({
          data: {
            id: n.data.id,
            label: n.data.label,
            node_type: n.data.node_type,
            color: NODE_COLORS[n.data.node_type] || "#94a3b8",
          },
        })),
        edges: edges.map((e) => ({
          data: {
            id: e.data.id,
            source: e.data.source,
            target: e.data.target,
            label: e.data.label || e.data.predicate || "",
            predicate: e.data.predicate,
          },
        })),
      },
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            "label": "data(label)",
            "color": "#e2e8f0",
            "font-size": "11px",
            "font-family": "Inter, sans-serif",
            "font-weight": "600",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": "6px",
            "text-background-color": "#0a0d14",
            "text-background-opacity": 0.7,
            "text-background-padding": "2px",
            "text-background-shape": "roundrectangle",
            "width": "42px",
            "height": "42px",
            "border-width": "2px",
            "border-color": "#1e2840",
            "border-opacity": 1,
          },
        },
        {
          selector: "node:selected",
          style: {
            "border-width": "3px",
            "border-color": "#e2e8f0",
            "width": "50px",
            "height": "50px",
          },
        },
        {
          selector: "edge",
          style: {
            "width": 2,
            "line-color": (ele) => EDGE_COLORS[ele.data("predicate")] || "#334155",
            "target-arrow-color": (ele) => EDGE_COLORS[ele.data("predicate")] || "#334155",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "label": "data(label)",
            "font-size": "9px",
            "font-family": "Inter, sans-serif",
            "color": "#64748b",
            "text-rotation": "autorotate",
            "text-background-color": "#0a0d14",
            "text-background-opacity": 0.8,
            "text-background-padding": "2px",
            "opacity": 0.8,
          },
        },
        {
          selector: "edge:selected",
          style: { "width": 3, "opacity": 1 },
        },
      ],
      layout: {
        name: "cose",
        idealEdgeLength: 120,
        nodeRepulsion: 8000,
        gravity: 0.3,
        animate: true,
        animationDuration: 800,
        fit: true,
        padding: 30,
      },
      wheelSensitivity: 0.3,
      minZoom: 0.3,
      maxZoom: 3,
    });

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      if (onNodeClick) onNodeClick(node.data());
    });

    cy.on("mouseover", "node", (evt) => {
      containerRef.current.style.cursor = "pointer";
    });
    cy.on("mouseout", "node", () => {
      containerRef.current.style.cursor = "default";
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [nodes, edges]);

  if (!nodes?.length) {
    return (
      <div className="card">
        <div className="card-title">
          <span className="dot" style={{ background: "#6366f1" }} />
          Network Graph
        </div>
        <div className="empty-state">
          <div className="empty-icon">🕸</div>
          <p>Graph will appear after analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: "1rem" }}>
      <div className="card-title" style={{ padding: "0 0.5rem 0.5rem" }}>
        <span className="dot" style={{ background: "#6366f1" }} />
        Network Graph — {nodes.length} nodes, {edges.length} edges
        <span style={{ marginLeft: "auto", fontSize: "0.7rem", color: "var(--text-muted)" }}>
          Click a node for details · Scroll to zoom · Drag to pan
        </span>
      </div>

      {/* Legend */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", padding: "0 0.5rem 0.75rem", borderBottom: "1px solid var(--border)", marginBottom: "0.75rem" }}>
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <span key={type} style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.68rem", color: "var(--text-secondary)" }}>
            <span style={{ width: 9, height: 9, borderRadius: "50%", background: color, display: "inline-block" }} />
            {type}
          </span>
        ))}
      </div>

      <div
        ref={containerRef}
        id="cytoscape-graph"
        style={{
          width: "100%",
          height: "460px",
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border)",
        }}
      />
    </div>
  );
}
