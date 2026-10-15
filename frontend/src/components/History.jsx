import { useState } from 'react';
import './History.css';

export default function History({ history, onClear }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('ALL');

  const total = history.length;
  const placed = history.filter((r) => r.prediction === 1).length;
  const notPlaced = total - placed;
  const placementRate = total > 0 ? ((placed / total) * 100).toFixed(1) : '0';

  const filtered = history.filter((item) => {
    // Status filter
    if (filter === 'PLACED' && item.prediction !== 1) return false;
    if (filter === 'NOT_PLACED' && item.prediction !== 0) return false;

    // Search query
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    const cgpa = String(item.inputs?.CGPA ?? '');
    const iq = String(item.inputs?.IQ ?? '');
    const status = String(item.status ?? '').toLowerCase();
    return cgpa.includes(term) || iq.includes(term) || status.includes(term);
  });

  function exportHistoryCSV() {
    if (history.length === 0) return;
    const headers = [
      'Record_ID',
      'Timestamp',
      'IQ',
      'Prev_Sem_Result',
      'CGPA',
      'Academic_Performance',
      'Extra_Curricular_Score',
      'Communication_Skills',
      'Projects_Completed',
      'Internship_Experience',
      'Prediction',
      'Status',
      'Placement_Probability'
    ];

    const rows = history.map((r, i) => [
      r.id || i + 1,
      r.timestamp,
      r.inputs?.IQ ?? '',
      r.inputs?.Prev_Sem_Result ?? '',
      r.inputs?.CGPA ?? '',
      r.inputs?.Academic_Performance ?? '',
      r.inputs?.Extra_Curricular_Score ?? '',
      r.inputs?.Communication_Skills ?? '',
      r.inputs?.Projects_Completed ?? '',
      r.inputs?.Internship_Experience ?? '',
      r.prediction,
      r.status,
      r.probability !== undefined ? (r.probability * 100).toFixed(1) + '%' : ''
    ]);

    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `placement_prediction_history_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleClear() {
    if (window.confirm('Are you sure you want to delete all prediction history records?')) {
      onClear();
    }
  }

  return (
    <div className="history-container animate-fade-in-up">
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">📜</span>
          <div>
            <h2>Prediction Audit History</h2>
            <p>Session and persistent local records of all individual and batch predictions evaluated</p>
          </div>
        </div>

        {total === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No predictions recorded yet</h3>
            <p style={{ marginTop: '0.5rem' }}>
              Run individual assessments or batch uploads to build candidate records here.
            </p>
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="history-stats-bar">
              <div className="metric-tile">
                <div className="metric-value">{total}</div>
                <div className="metric-label">Total Inferences</div>
              </div>
              <div className="metric-tile">
                <div className="metric-value" style={{ color: 'var(--accent-emerald)' }}>
                  {placed}
                </div>
                <div className="metric-label">Predicted Placed</div>
              </div>
              <div className="metric-tile">
                <div className="metric-value" style={{ color: 'var(--accent-rose)' }}>
                  {notPlaced}
                </div>
                <div className="metric-label">Predicted At-Risk</div>
              </div>
              <div className="metric-tile">
                <div className="metric-value">{placementRate}%</div>
                <div className="metric-label">Placement Ratio</div>
              </div>
            </div>

            {/* Toolbar */}
            <div className="history-toolbar">
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', flex: 1 }}>
                <div className="search-box">
                  <span>🔍</span>
                  <input
                    type="text"
                    placeholder="Search by CGPA, IQ, or status..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>

                <div className="filter-pills">
                  <button
                    type="button"
                    className={`filter-pill ${filter === 'ALL' ? 'active' : ''}`}
                    onClick={() => setFilter('ALL')}
                  >
                    All ({total})
                  </button>
                  <button
                    type="button"
                    className={`filter-pill ${filter === 'PLACED' ? 'active' : ''}`}
                    onClick={() => setFilter('PLACED')}
                  >
                    Placed ({placed})
                  </button>
                  <button
                    type="button"
                    className={`filter-pill ${filter === 'NOT_PLACED' ? 'active' : ''}`}
                    onClick={() => setFilter('NOT_PLACED')}
                  >
                    Not Placed ({notPlaced})
                  </button>
                </div>
              </div>

              <div className="history-actions">
                <button type="button" className="btn btn-outline" onClick={exportHistoryCSV}>
                  📥 Export CSV
                </button>
                <button type="button" className="btn btn-danger" onClick={handleClear}>
                  🗑️ Clear All
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>IQ</th>
                    <th>CGPA</th>
                    <th>Prev Sem</th>
                    <th>Acad / Comm</th>
                    <th>Projects</th>
                    <th>Internship</th>
                    <th>Status</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        No records match your search filter.
                      </td>
                    </tr>
                  ) : (
                    filtered.map((item) => {
                      const probPct = Math.round((item.probability ?? (item.prediction === 1 ? 0.85 : 0.25)) * 100);
                      const isSuccess = item.prediction === 1;
                      const timeStr = item.timestamp
                        ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : '—';

                      return (
                        <tr key={item.id}>
                          <td>{timeStr}</td>
                          <td>{item.inputs?.IQ ?? '—'}</td>
                          <td><strong>{item.inputs?.CGPA !== undefined ? Number(item.inputs.CGPA).toFixed(2) : '—'}</strong></td>
                          <td>{item.inputs?.Prev_Sem_Result !== undefined ? Number(item.inputs.Prev_Sem_Result).toFixed(2) : '—'}</td>
                          <td>
                            {item.inputs?.Academic_Performance ?? '—'} / {item.inputs?.Communication_Skills ?? '—'}
                          </td>
                          <td>{item.inputs?.Projects_Completed ?? '—'}</td>
                          <td>{item.inputs?.Internship_Experience === 1 ? 'Yes' : 'No'}</td>
                          <td>
                            <span className={`badge ${isSuccess ? 'badge-success' : 'badge-danger'}`}>
                              {item.status}
                            </span>
                          </td>
                          <td>
                            <div className="prob-cell">
                              <div className="mini-bar">
                                <div
                                  className="mini-fill"
                                  style={{
                                    width: `${probPct}%`,
                                    background: isSuccess ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                                  }}
                                />
                              </div>
                              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: isSuccess ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                                {probPct}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
