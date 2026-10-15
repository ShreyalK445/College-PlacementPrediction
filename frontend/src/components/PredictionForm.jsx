import { useState } from 'react';
import './PredictionForm.css';
import { predictSingle } from '../api';

const DEFAULT_VALUES = {
  IQ: 110,
  Prev_Sem_Result: 7.5,
  CGPA: 7.6,
  Academic_Performance: 7,
  Extra_Curricular_Score: 6,
  Communication_Skills: 7,
  Projects_Completed: 2,
  Internship_Experience: 1,
};

const PRESETS = [
  {
    name: '🌟 High Achiever',
    values: {
      IQ: 125,
      Prev_Sem_Result: 8.9,
      CGPA: 8.8,
      Academic_Performance: 9,
      Extra_Curricular_Score: 8,
      Communication_Skills: 9,
      Projects_Completed: 4,
      Internship_Experience: 1,
    },
  },
  {
    name: '⚖️ Balanced Candidate',
    values: {
      IQ: 108,
      Prev_Sem_Result: 7.4,
      CGPA: 7.5,
      Academic_Performance: 7,
      Extra_Curricular_Score: 6,
      Communication_Skills: 7,
      Projects_Completed: 2,
      Internship_Experience: 1,
    },
  },
  {
    name: '⚠️ Borderline / At-Risk',
    values: {
      IQ: 92,
      Prev_Sem_Result: 5.6,
      CGPA: 5.8,
      Academic_Performance: 5,
      Extra_Curricular_Score: 4,
      Communication_Skills: 5,
      Projects_Completed: 0,
      Internship_Experience: 0,
    },
  },
];

export default function PredictionForm({ modelInfo, onResult, onNavigate }) {
  const [formData, setFormData] = useState(DEFAULT_VALUES);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  function handleChange(field, value) {
    setFormData((prev) => ({
      ...prev,
      [field]: typeof value === 'string' ? parseFloat(value) : value,
    }));
  }

  function applyPreset(presetValues) {
    setFormData(presetValues);
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        IQ: Number(formData.IQ),
        Prev_Sem_Result: Number(formData.Prev_Sem_Result),
        CGPA: Number(formData.CGPA),
        Academic_Performance: Math.round(Number(formData.Academic_Performance)),
        Extra_Curricular_Score: Math.round(Number(formData.Extra_Curricular_Score)),
        Communication_Skills: Math.round(Number(formData.Communication_Skills)),
        Projects_Completed: Math.round(Number(formData.Projects_Completed)),
        Internship_Experience: Number(formData.Internship_Experience),
      };

      // Request prediction with explain=true for tree-path attribution
      const response = await predictSingle(payload, true);
      const predictionData = response.data.results;
      setResult(predictionData);

      if (onResult) {
        onResult({
          id: Date.now() + Math.random().toString(36).substr(2, 4),
          timestamp: new Date().toISOString(),
          inputs: { ...payload },
          prediction: predictionData.placement_prediction,
          status: predictionData.status,
          probability: predictionData.placement_probability ?? (predictionData.placement_prediction === 1 ? 0.85 : 0.25),
          explainability: predictionData.explainability,
        });
      }
    } catch (err) {
      setError(err.message || 'Prediction failed. Ensure the backend server is running.');
    } finally {
      setLoading(false);
    }
  }

  function getInsights() {
    const tips = [];
    if (formData.CGPA < 7.0) {
      tips.push('Target raising cumulative GPA above 7.0 to pass tier-1 enterprise eligibility filters.');
    } else {
      tips.push('Cumulative GPA is strong and clears campus recruitment eligibility bars.');
    }

    if (formData.Communication_Skills < 7) {
      tips.push('Mock interview prep & GD practice recommended to elevate communication score.');
    }

    if (formData.Projects_Completed < 2) {
      tips.push('Build at least 2 full-stack or domain-specific projects to showcase in technical rounds.');
    }

    if (formData.Internship_Experience === 0) {
      tips.push('Completing an industrial internship or open-source fellowship significantly boosts conversion.');
    }

    return tips;
  }

  const isPlaced = result?.placement_prediction === 1;
  const probability = result?.placement_probability !== undefined
    ? Math.round(result.placement_probability * 100)
    : (isPlaced ? 85 : 25);

  const explain = result?.explainability;

  return (
    <div className="prediction-container animate-fade-in-up">
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">🔮</span>
          <div style={{ flex: 1 }}>
            <h2>Candidate Assessment</h2>
            <p>Enter academic parameters to compute real-time placement probability and explainable AI factors</p>
          </div>
          {modelInfo?.model_version && (
            <span className="badge badge-warning">
              {modelInfo.model_version}
            </span>
          )}
        </div>

        {/* Preset Profiles */}
        <div className="preset-pills">
          <span className="preset-label">Load Preset Profile:</span>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className="preset-btn"
              onClick={() => applyPreset(p.values)}
            >
              {p.name}
            </button>
          ))}
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {/* IQ */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🧠 IQ Score</label>
                <span className="input-val-badge">{formData.IQ}</span>
              </div>
              <input
                type="range"
                min="60"
                max="160"
                step="1"
                value={formData.IQ}
                onChange={(e) => handleChange('IQ', e.target.value)}
              />
              <div className="input-hint">
                <span>60</span>
                <span>Average: 100–115</span>
                <span>160</span>
              </div>
            </div>

            {/* CGPA */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🎓 Cumulative GPA (CGPA)</label>
                <span className="input-val-badge">{Number(formData.CGPA).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="4.0"
                max="10.0"
                step="0.05"
                value={formData.CGPA}
                onChange={(e) => handleChange('CGPA', e.target.value)}
              />
              <div className="input-hint">
                <span>4.0</span>
                <span>Scale: 10.0</span>
                <span>10.0</span>
              </div>
            </div>

            {/* Previous Semester Result */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>📑 Previous Sem GPA</label>
                <span className="input-val-badge">{Number(formData.Prev_Sem_Result).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="4.0"
                max="10.0"
                step="0.05"
                value={formData.Prev_Sem_Result}
                onChange={(e) => handleChange('Prev_Sem_Result', e.target.value)}
              />
              <div className="input-hint">
                <span>4.0</span>
                <span>Semester consistency</span>
                <span>10.0</span>
              </div>
            </div>

            {/* Academic Performance */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>📚 Academic Rating</label>
                <span className="input-val-badge">{formData.Academic_Performance} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={formData.Academic_Performance}
                onChange={(e) => handleChange('Academic_Performance', e.target.value)}
              />
              <div className="input-hint">
                <span>1 (Weak)</span>
                <span>Faculty assessment</span>
                <span>10 (Exemplary)</span>
              </div>
            </div>

            {/* Communication Skills */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🗣️ Communication Skills</label>
                <span className="input-val-badge">{formData.Communication_Skills} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={formData.Communication_Skills}
                onChange={(e) => handleChange('Communication_Skills', e.target.value)}
              />
              <div className="input-hint">
                <span>1</span>
                <span>Verbal & Soft Skills</span>
                <span>10</span>
              </div>
            </div>

            {/* Extra-Curricular Score */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>🏆 Extra-Curricular Score</label>
                <span className="input-val-badge">{formData.Extra_Curricular_Score} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={formData.Extra_Curricular_Score}
                onChange={(e) => handleChange('Extra_Curricular_Score', e.target.value)}
              />
              <div className="input-hint">
                <span>1</span>
                <span>Clubs, Sports & Events</span>
                <span>10</span>
              </div>
            </div>

            {/* Projects Completed */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>💻 Projects Completed</label>
                <span className="input-val-badge">{formData.Projects_Completed}</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                step="1"
                value={formData.Projects_Completed}
                onChange={(e) => handleChange('Projects_Completed', e.target.value)}
              />
              <div className="input-hint">
                <span>0</span>
                <span>Technical Capstones</span>
                <span>10+</span>
              </div>
            </div>

            {/* Internship Experience */}
            <div className="input-slider-box">
              <div className="input-header">
                <label>💼 Internship Experience</label>
                <span className="input-val-badge">
                  {formData.Internship_Experience === 1 ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="toggle-group" style={{ marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className={`toggle-option ${formData.Internship_Experience === 1 ? 'active' : ''}`}
                  onClick={() => handleChange('Internship_Experience', 1)}
                >
                  ✓ Yes (Completed)
                </button>
                <button
                  type="button"
                  className={`toggle-option ${formData.Internship_Experience === 0 ? 'active' : ''}`}
                  onClick={() => handleChange('Internship_Experience', 0)}
                >
                  ✕ None
                </button>
              </div>
              <div className="input-hint" style={{ marginTop: '0.75rem' }}>
                <span>Prior industrial / company tenure</span>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => {
                setFormData(DEFAULT_VALUES);
                setResult(null);
                setError(null);
              }}
            >
              Reset
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" /> Evaluating Profile...
                </>
              ) : (
                <>🚀 Run Placement Prediction</>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Prediction Result Presentation */}
      {result && (
        <div className="glass-card result-card animate-fade-in-up">
          <div className="result-header">
            <div className="result-status-title">
              <span style={{ fontSize: '2rem' }}>{isPlaced ? '🎉' : '📈'}</span>
              <div>
                <h3 style={{ color: isPlaced ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
                  {isPlaced ? 'Placement Likely — Candidate Approved' : 'Placement Risk — Action Required'}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Classification Output: {result.status}
                </p>
              </div>
            </div>
            <span className={`badge ${isPlaced ? 'badge-success' : 'badge-warning'}`}>
              {result.status}
            </span>
          </div>

          <div className="result-body">
            {/* Probability Progress Meter */}
            <div className="prob-meter-container">
              <div className="prob-label-row">
                <span style={{ color: 'var(--text-secondary)' }}>Model Placement Probability:</span>
                <span style={{ color: isPlaced ? 'var(--accent-emerald)' : 'var(--accent-rose)', fontWeight: 700 }}>
                  {probability}% Confidence
                </span>
              </div>
              <div className="prob-track">
                <div
                  className={`prob-fill ${isPlaced ? 'high' : 'low'}`}
                  style={{ width: `${probability}%` }}
                />
              </div>
            </div>

            {/* Explainable AI Factor Contributions */}
            {explain && (
              <div className="glass-card" style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem' }}>
                <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>🔍</span> Explainable AI — Local Feature Attribution (Tree Decomposition)
                </h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  Base Prior Probability: <strong>{Math.round(explain.base_value * 100)}%</strong>. Below is how each individual feature shifted this candidate's probability from the baseline:
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  {/* Top Positives */}
                  <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: 'var(--radius-sm)', padding: '0.75rem' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--accent-emerald)', marginBottom: '0.5rem' }}>
                      ▲ Strongest Positive Drivers:
                    </div>
                    {explain.top_positive_factors?.slice(0, 3).map((f) => (
                      <div key={f.feature} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', padding: '0.2rem 0' }}>
                        <span>{f.label} ({f.student_value})</span>
                        <strong style={{ color: 'var(--accent-emerald)' }}>+{f.percentage_impact}%</strong>
                      </div>
                    ))}
                  </div>

                  {/* Top Negatives */}
                  <div style={{ background: 'rgba(244, 63, 94, 0.06)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: 'var(--radius-sm)', padding: '0.75rem' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--accent-rose)', marginBottom: '0.5rem' }}>
                      ▼ Limiting Factors / Score Drags:
                    </div>
                    {explain.top_negative_factors?.slice(0, 3).map((f) => (
                      <div key={f.feature} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', padding: '0.2rem 0' }}>
                        <span>{f.label} ({f.student_value})</span>
                        <strong style={{ color: 'var(--accent-rose)' }}>{f.percentage_impact}%</strong>
                      </div>
                    ))}
                    {(!explain.top_negative_factors || explain.top_negative_factors.length === 0) && (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None — all features performed above average.</span>
                    )}
                  </div>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', borderTop: '1px solid var(--border-glass)', paddingTop: '0.5rem' }}>
                  {explain.disclaimer}
                </div>
              </div>
            )}

            {/* AI Insights & Recommendations */}
            <div className="insights-box">
              <h4>📋 Career Readiness Diagnostic & Recommendations</h4>
              <ul>
                {getInsights().map((tip, idx) => (
                  <li key={idx}>{tip}</li>
                ))}
              </ul>
            </div>

            {/* Quick Actions into other Modules */}
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', paddingTop: '0.5rem' }}>
              {onNavigate && (
                <>
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={() => onNavigate('simulator', formData)}
                  >
                    🧪 Test in What-If Simulator
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={() => onNavigate('roadmap', formData)}
                  >
                    🗺️ Generate 8-Week Roadmap
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={() => onNavigate('roles', formData)}
                  >
                    🎯 Match Target Job Roles
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
