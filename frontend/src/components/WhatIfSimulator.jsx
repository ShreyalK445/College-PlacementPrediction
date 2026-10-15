import { useState } from 'react';
import './WhatIfSimulator.css';
import { runSimulation } from '../api';

const DEFAULT_BASELINE = {
  IQ: 105,
  Prev_Sem_Result: 6.8,
  CGPA: 6.9,
  Academic_Performance: 6,
  Extra_Curricular_Score: 5,
  Communication_Skills: 6,
  Projects_Completed: 1,
  Internship_Experience: 0,
};

export default function WhatIfSimulator({ initialProfile, onGenerateRoadmap }) {
  const [baseline, setBaseline] = useState(initialProfile || DEFAULT_BASELINE);
  const [hypo, setHypo] = useState({
    ...(initialProfile || DEFAULT_BASELINE),
    Communication_Skills: Math.min(10, (initialProfile || DEFAULT_BASELINE).Communication_Skills + 2),
    Projects_Completed: Math.min(10, (initialProfile || DEFAULT_BASELINE).Projects_Completed + 2),
    Internship_Experience: 1,
  });

  const [loading, setLoading] = useState(false);
  const [simResult, setSimResult] = useState(null);
  const [error, setError] = useState(null);

  function handleHypoChange(field, value) {
    setHypo((prev) => ({
      ...prev,
      [field]: typeof value === 'string' ? parseFloat(value) : value,
    }));
  }

  async function handleSimulate(e) {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await runSimulation(baseline, hypo);
      setSimResult(res.data);
    } catch (err) {
      setError(err.message || 'Simulation failed.');
    } finally {
      setLoading(false);
    }
  }

  function syncHypoToBaseline() {
    setBaseline({ ...hypo });
    setSimResult(null);
  }

  return (
    <div className="simulator-container animate-fade-in-up">
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">🧪</span>
          <div>
            <h2>What-If Placement Simulator</h2>
            <p>Adjust hypothetical credentials to simulate marginal placement confidence shifts before real recruitment drives</p>
          </div>
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSimulate}>
          <div className="form-grid">
            {/* Communication Skills */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🗣️ Communication Skills</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Base: {baseline.Communication_Skills}</span>
                  <span className="input-val-badge">Sim: {hypo.Communication_Skills}</span>
                </div>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={hypo.Communication_Skills}
                onChange={(e) => handleHypoChange('Communication_Skills', e.target.value)}
              />
              <div className="input-hint">
                <span>1</span>
                <span>Model weight: 27.89%</span>
                <span>10</span>
              </div>
            </div>

            {/* Projects Completed */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>💻 Projects Completed</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Base: {baseline.Projects_Completed}</span>
                  <span className="input-val-badge">Sim: {hypo.Projects_Completed}</span>
                </div>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                step="1"
                value={hypo.Projects_Completed}
                onChange={(e) => handleHypoChange('Projects_Completed', e.target.value)}
              />
              <div className="input-hint">
                <span>0</span>
                <span>Model weight: 16.83%</span>
                <span>10</span>
              </div>
            </div>

            {/* Cumulative GPA */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🎓 Cumulative GPA (CGPA)</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Base: {Number(baseline.CGPA).toFixed(2)}</span>
                  <span className="input-val-badge">Sim: {Number(hypo.CGPA).toFixed(2)}</span>
                </div>
              </div>
              <input
                type="range"
                min="4.0"
                max="10.0"
                step="0.05"
                value={hypo.CGPA}
                onChange={(e) => handleHypoChange('CGPA', e.target.value)}
              />
              <div className="input-hint">
                <span>4.0</span>
                <span>Academic qualification</span>
                <span>10.0</span>
              </div>
            </div>

            {/* Internship Experience */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>💼 Internship Experience</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Base: {baseline.Internship_Experience === 1 ? 'Yes' : 'No'}</span>
                  <span className="input-val-badge">Sim: {hypo.Internship_Experience === 1 ? 'Yes' : 'No'}</span>
                </div>
              </div>
              <div className="toggle-group" style={{ marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className={`toggle-option ${hypo.Internship_Experience === 1 ? 'active' : ''}`}
                  onClick={() => handleHypoChange('Internship_Experience', 1)}
                >
                  ✓ Yes (Completed)
                </button>
                <button
                  type="button"
                  className={`toggle-option ${hypo.Internship_Experience === 0 ? 'active' : ''}`}
                  onClick={() => handleHypoChange('Internship_Experience', 0)}
                >
                  ✕ None
                </button>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={syncHypoToBaseline}
            >
              Set Current as New Baseline
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" /> Calculating Scenario...
                </>
              ) : (
                <>⚡ Run Scenario Simulation</>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Simulation Result Presentation */}
      {simResult && (
        <div className="glass-card animate-fade-in-up">
          <div className="section-header">
            <span className="icon">📊</span>
            <div>
              <h2>Simulation Outcome & Impact Analysis</h2>
              <p>{simResult.delta.status_transition}</p>
            </div>
          </div>

          {/* Comparison Cards */}
          <div className="sim-comparison-grid" style={{ marginBottom: '1.5rem' }}>
            {/* Baseline */}
            <div className="sim-metric-card baseline">
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Current Baseline</span>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--text-primary)' }}>
                {Math.round(simResult.baseline.probability * 100)}%
              </div>
              <span className={`badge ${simResult.baseline.status === 'Placed' ? 'badge-success' : 'badge-danger'}`} style={{ marginTop: '0.5rem' }}>
                {simResult.baseline.status}
              </span>
            </div>

            {/* Hypothetical */}
            <div className="sim-metric-card hypothetical">
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>Hypothetical Scenario</span>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--accent-cyan)' }}>
                {Math.round(simResult.hypothetical.probability * 100)}%
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center' }}>
                <span className={`badge ${simResult.hypothetical.status === 'Placed' ? 'badge-success' : 'badge-danger'}`}>
                  {simResult.hypothetical.status}
                </span>
                <span className={`delta-badge ${simResult.delta.percentage_delta >= 0 ? 'positive' : 'negative'}`}>
                  {simResult.delta.percentage_delta >= 0 ? '+' : ''}{simResult.delta.percentage_delta}% Shift
                </span>
              </div>
            </div>
          </div>

          {/* Modified Features Breakdown */}
          {simResult.modified_features?.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                Parameters Modified in this Simulation:
              </h4>
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Original</th>
                      <th>Simulated</th>
                      <th>Delta</th>
                      <th>Marginal Probability Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    {simResult.modified_features.map((m) => (
                      <tr key={m.feature}>
                        <td><strong>{m.label}</strong></td>
                        <td>{m.original_value}</td>
                        <td><span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{m.hypothetical_value}</span></td>
                        <td>{m.delta_value > 0 ? `+${m.delta_value}` : m.delta_value}</td>
                        <td>
                          <span style={{ fontWeight: 700, color: m.delta_contribution >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                            {m.delta_contribution >= 0 ? '+' : ''}{Math.round(m.delta_contribution * 100)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* AI Insights & Next Steps */}
          <div className="insights-box" style={{ marginBottom: '1.25rem' }}>
            <h4>💡 Simulation Insights</h4>
            <ul>
              {simResult.insights.map((ins, idx) => (
                <li key={idx}>{ins}</li>
              ))}
            </ul>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', maxWidth: '600px' }}>
              {simResult.disclaimer}
            </span>
            {onGenerateRoadmap && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => onGenerateRoadmap(hypo)}
              >
                🗺️ Create Roadmap for this Target Profile
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
