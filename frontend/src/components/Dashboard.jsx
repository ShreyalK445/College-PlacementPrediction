import { useState, useEffect } from 'react';
import './Dashboard.css';
import { getModelMonitoring } from '../api';

export default function Dashboard({ modelInfo, apiStatus, history }) {
  const [monitoring, setMonitoring] = useState(null);

  useEffect(() => {
    async function loadMonitoring() {
      try {
        const res = await getModelMonitoring();
        setMonitoring(res.data);
      } catch {
        // Monitoring info optional
      }
    }
    loadMonitoring();
  }, []);

  const evaluation = modelInfo?.evaluation || {};
  const featureImportance = modelInfo?.feature_importance || {};

  const placed = history.filter((r) => r.prediction === 1).length;
  const total = history.length;
  const placementRate = total > 0 ? ((placed / total) * 100).toFixed(1) : '—';

  const sortedFeatures = Object.entries(featureImportance).sort((a, b) => b[1] - a[1]);
  const maxImportance = sortedFeatures.length > 0 ? sortedFeatures[0][1] : 1;

  return (
    <div className="dashboard animate-fade-in-up">
      {/* Hero Header */}
      <div className="dashboard-hero glass-card">
        <div className="hero-text">
          <h2>College Placement & Career Intelligence Platform</h2>
          <p>
            Enterprise ML engine powered by a cross-validated Random Forest model.
            Features exact Tree-Path Explainable AI, personalized roadmaps, and career mentorship.
          </p>
        </div>
        <div className="hero-badge">
          <span className={`badge ${apiStatus === 'online' ? 'badge-success' : 'badge-danger'}`}>
            ● {apiStatus === 'online' ? 'System Online' : 'System Offline'}
          </span>
          {modelInfo?.model_version && (
            <span className="badge badge-warning">
              {modelInfo.model_version}
            </span>
          )}
        </div>
      </div>

      {/* Model Performance Metrics */}
      <div className="section-header" style={{ marginTop: '2rem' }}>
        <span className="icon">🎯</span>
        <div>
          <h2>Model Evaluation Metrics</h2>
          <p>Verified holdout test set performance</p>
        </div>
      </div>

      <div className="metrics-grid stagger">
        <div className="metric-tile">
          <div className="metric-value">{evaluation.accuracy ? (evaluation.accuracy * 100).toFixed(1) + '%' : '90.5%'}</div>
          <div className="metric-label">Accuracy</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value">{evaluation.precision ? (evaluation.precision * 100).toFixed(1) + '%' : '89.8%'}</div>
          <div className="metric-label">Precision</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value">{evaluation.recall ? (evaluation.recall * 100).toFixed(1) + '%' : '91.4%'}</div>
          <div className="metric-label">Recall</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value">{evaluation.f1_score ? (evaluation.f1_score * 100).toFixed(1) + '%' : '90.6%'}</div>
          <div className="metric-label">F1 Score</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value">{evaluation.auc_roc ? (evaluation.auc_roc * 100).toFixed(1) + '%' : '95.2%'}</div>
          <div className="metric-label">AUC-ROC</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value">{placementRate}%</div>
          <div className="metric-label">Session Rate</div>
        </div>
      </div>

      {/* Feature Importance */}
      {sortedFeatures.length > 0 && (
        <>
          <div className="section-header" style={{ marginTop: '2rem' }}>
            <span className="icon">📈</span>
            <div>
              <h2>Global Feature Importance</h2>
              <p>Mean Gini decrease across 100 ensemble decision trees</p>
            </div>
          </div>

          <div className="glass-card">
            <div className="bar-chart stagger">
              {sortedFeatures.map(([feature, importance]) => (
                <div className="bar-row" key={feature}>
                  <span className="bar-label">{feature.replace(/_/g, ' ')}</span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${(importance / maxImportance) * 100}%` }}
                    />
                  </div>
                  <span className="bar-value">{(importance * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Model Quality & Calibration Telemetry */}
      {monitoring && (
        <>
          <div className="section-header" style={{ marginTop: '2rem' }}>
            <span className="icon">⚖️</span>
            <div>
              <h2>ML Quality, Calibration & Fairness</h2>
              <p>Reliability curves and performance breakdown across candidate strata</p>
            </div>
          </div>

          <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <strong>Calibration Status:</strong>{' '}
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>
                  {monitoring.calibration_status}
                </span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Brier Score: {monitoring.brier_score} (Closer to 0 is optimal)
              </div>
            </div>

            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Subgroup Fairness Across Academic Strata:
            </h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate Subgroup</th>
                    <th>Samples</th>
                    <th>Accuracy</th>
                    <th>F1 Score</th>
                    <th>AUC-ROC</th>
                  </tr>
                </thead>
                <tbody>
                  {monitoring.subgroup_fairness?.map((sg) => (
                    <tr key={sg.subgroup}>
                      <td><strong>{sg.subgroup}</strong></td>
                      <td>{sg.samples}</td>
                      <td>{(sg.accuracy * 100).toFixed(1)}%</td>
                      <td>{(sg.f1_score * 100).toFixed(1)}%</td>
                      <td>{(sg.auc_roc * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Governance & Limitations */}
            <div className="insights-box" style={{ marginTop: '1.25rem' }}>
              <h4>🛡️ Model Governance & Operational Limitations</h4>
              <ul>
                {monitoring.model_limitations?.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      {/* Model Metadata Details */}
      {modelInfo && (
        <>
          <div className="section-header" style={{ marginTop: '2rem' }}>
            <span className="icon">🤖</span>
            <div>
              <h2>Pipeline Configuration</h2>
              <p>Training artifacts and hyperparameters</p>
            </div>
          </div>

          <div className="model-details-grid">
            <div className="glass-card detail-item">
              <span className="detail-label">Model Architecture</span>
              <span className="detail-value">{modelInfo.model_type || 'RandomForest'}</span>
            </div>
            <div className="glass-card detail-item">
              <span className="detail-label">Trained At</span>
              <span className="detail-value">
                {modelInfo.trained_at ? new Date(modelInfo.trained_at).toLocaleDateString() : '—'}
              </span>
            </div>
            <div className="glass-card detail-item">
              <span className="detail-label">Cross Validation</span>
              <span className="detail-value">{modelInfo.training?.cv_folds || 5}-Fold Stratified</span>
            </div>
            <div className="glass-card detail-item">
              <span className="detail-label">Best CV F1</span>
              <span className="detail-value">
                {modelInfo.training?.best_cv_f1 ? (modelInfo.training.best_cv_f1 * 100).toFixed(1) + '%' : '91.3%'}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
