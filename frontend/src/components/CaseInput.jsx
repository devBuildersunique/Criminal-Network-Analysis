import { useState } from "react";
import { analyzeCase } from "../api";

const DEMO_TEXT =
  "Rahul Sharma met Amit Kumar in Delhi on 25 August. " +
  "Rahul contacted Amit 42 times in two days using phone 9876543210. " +
  "Rahul transferred Rs 850000 to Amit. " +
  "Rahul used vehicle DL01AB1234. " +
  "Rahul was previously mentioned in Case C102 with Ravi Singh.";

function getUserFriendlyError(err, health) {
  // Backend offline
  if (!err?.response) {
    return (
      "Cannot reach backend server. " +
      "Make sure the FastAPI server is running: uvicorn backend.main:app --reload --port 8000"
    );
  }
  const status = err.response?.status;
  const detail = err.response?.data?.detail;

  if (status === 400) {
    if (detail?.toLowerCase().includes("empty")) {
      return "Case text cannot be empty. Please enter a case statement before analyzing.";
    }
    return `Invalid request: ${detail || "Please check your input."}`;
  }
  if (status === 422) {
    return "The case text could not be processed. Please check formatting and try again.";
  }
  if (status === 500) {
    return (
      "The analysis pipeline encountered an internal error. " +
      "This may be a temporary issue — please try again or reload the page."
    );
  }
  return detail || "Analysis failed. Please try again.";
}

export default function CaseInput({ onResult, onLoading, health }) {
  const [text, setText]     = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);
  const [noEntities, setNoEntities] = useState(false);

  const loadDemo = () => {
    setText(DEMO_TEXT);
    setError(null);
    setNoEntities(false);
  };

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError("Please enter a case statement before analyzing.");
      return;
    }
    setLoading(true);
    setError(null);
    setNoEntities(false);
    onLoading(true);
    try {
      const result = await analyzeCase(text);
      if (!result.entities || result.entities.length === 0) {
        setNoEntities(true);
        onResult(null);
      } else {
        onResult(result);
      }
    } catch (e) {
      setError(getUserFriendlyError(e, health));
      onResult(null);
    } finally {
      setLoading(false);
      onLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setError(null);
    setNoEntities(false);
    onResult(null);
  };

  const backendOffline = health !== null && health?.status !== "ok" && health?.database === undefined;

  return (
    <div className="card">
      <div className="card-title">
        <span className="dot" style={{ background: "#6366f1" }} />
        Case Statement Input
      </div>

      <textarea
        id="case-input"
        className="case-textarea"
        placeholder={
          "Enter a case statement...\n\n" +
          "Example: \"Rahul Sharma met Amit Kumar in Delhi on 25 August...\"\n\n" +
          "Click [Load Demo] to use the pre-built demonstration case."
        }
        value={text}
        onChange={(e) => { setText(e.target.value); setError(null); setNoEntities(false); }}
        rows={7}
        disabled={loading}
      />

      <div style={{
        display: "flex", gap: "0.75rem", marginTop: "1rem",
        alignItems: "center", flexWrap: "wrap",
      }}>
        <button
          id="btn-analyze"
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={loading || !text.trim()}
        >
          {loading ? <><span className="spinner" /> Analyzing...</> : "⚡ Analyze Case"}
        </button>

        <button
          id="btn-demo"
          className="btn btn-secondary"
          onClick={loadDemo}
          disabled={loading}
        >
          📋 Load Demo
        </button>

        <button
          className="btn btn-secondary"
          onClick={handleClear}
          disabled={loading}
        >
          ✕ Clear
        </button>

        <span style={{ marginLeft: "auto", fontSize: "0.72rem", color: "var(--text-muted)" }}>
          {text.length} characters
        </span>
      </div>

      {/* Error banner */}
      {error && (
        <div className="error-banner" style={{ marginTop: "1rem" }}>
          <span>⚠</span>
          <span>{error}</span>
        </div>
      )}

      {/* No entities extracted */}
      {noEntities && !error && (
        <div style={{
          marginTop: "1rem", padding: "0.75rem 1rem",
          background: "rgba(245,158,11,0.08)",
          border: "1px solid rgba(245,158,11,0.25)",
          borderRadius: "var(--radius-sm)",
          fontSize: "0.82rem", color: "#fbbf24",
          display: "flex", gap: "0.5rem",
        }}>
          <span>ℹ</span>
          <span>
            No entities were extracted from the case text. Try including names of people,
            locations, phone numbers, vehicle plates, or case IDs.
            Example: <em>Rahul Sharma met Amit Kumar in Delhi using phone 9876543210.</em>
          </span>
        </div>
      )}

      {/* Backend offline warning */}
      {health !== null && !health && (
        <div className="error-banner" style={{ marginTop: "0.75rem" }}>
          <span>⚠</span>
          <span>
            Backend server is offline. Start it with:{" "}
            <code style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "0.78rem" }}>
              uvicorn backend.main:app --reload --port 8000
            </code>
          </span>
        </div>
      )}
    </div>
  );
}
