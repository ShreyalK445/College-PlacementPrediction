import { useState, useEffect } from 'react';
import './TPODashboardView.css';
import { getTPOCohort, getTPOInterventions, recordTPOIntervention, getTPOCSVExportUrl } from '../api';

export default function TPODashboardView() {
  const [cohortData, setCohortData] = useState(null);
  const [interventions, setInterventions] = useState([]);
  const [department, setDepartment] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Intervention Modal State
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [reason, setReason] = useState('');
  const [actionPlan, setActionPlan] = useState('');
  const [followUpDate, setFollowUpDate] = useState('2026-11-01');
  const [savingIntervention, setSavingIntervention] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [cRes, iRes] = await Promise.all([
          getTPOCohort(department === 'ALL' ? '' : department),
          getTPOInterventions(),
        ]);
        setCohortData(cRes.data);
        setInterventions(iRes.data.interventions || []);
      } catch (err) {
        setError(err.message || 'Failed to load TPO cohort data.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [department]);

  async function handleSaveIntervention(e) {
    e.preventDefault();
    if (!selectedStudent || !reason || !actionPlan) return;
    setSavingIntervention(true);

    try {
      const payload = {
        student_name: selectedStudent.name,
        student_email: selectedStudent.email,
        priority: selectedStudent.intervention_priority,
        reason,
        action_plan: actionPlan,
        follow_up_date: followUpDate,
      };
      await recordTPOIntervention(payload);

      // Refresh list
      const iRes = await getTPOInterventions();
      setInterventions(iRes.data.interventions || []);
      setSelectedStudent(null);
      setReason('');
      setActionPlan('');
    } catch (err) {
      alert('Failed to save intervention: ' + err.message);
    } finally {
      setSavingIntervention(false);
    }
  }

  const metrics = cohortData?.cohort_metrics || {};
  const rawRoster = cohortData?.roster || [];

  const filteredRoster = rawRoster.filter((r) => {
    if (priorityFilter !== 'ALL' && r.intervention_priority !== priorityFilter) return false;
    return true;
  });

  return (
    <div className="tpo-container animate-fade-in-up">
      {/* Header */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div className="section-header" style={{ marginBottom: 0 }}>
            <span className="icon">🏛️</span>
            <div>
              <h2>Training & Placement Officer (TPO) Early-Warning Dashboard</h2>
              <p>Cohort triage board prioritizing remedial interventions, counselor actions, and placement tracking</p>
            </div>
          </div>

          <a
            href={getTPOCSVExportUrl(department === 'ALL' ? '' : department)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline"
          >
            📥 Export Cohort Report (CSV)
          </a>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Cohort Metric Tiles */}
      <div className="tpo-metrics-row">
        <div className="metric-tile">
          <div className="metric-value">{metrics.total_students || 0}</div>
          <div className="metric-label">Total Cohort</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value" style={{ color: 'var(--accent-rose)' }}>
            {metrics.high_priority_interventions || 0}
          </div>
          <div className="metric-label">High Priority At-Risk</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value" style={{ color: 'var(--accent-amber)' }}>
            {metrics.medium_priority_interventions || 0}
          </div>
          <div className="metric-label">Moderate Triage</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value" style={{ color: 'var(--accent-emerald)' }}>
            {metrics.on_track_students || 0}
          </div>
          <div className="metric-label">On-Track Placed</div>
        </div>
        <div className="metric-tile">
          <div className="metric-value" style={{ color: 'var(--accent-cyan)' }}>
            {metrics.cohort_placement_rate || 0}%
          </div>
          <div className="metric-label">Cohort Placement Rate</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          {/* Department Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Department:</span>
            {['ALL', 'Computer Science', 'Information Technology', 'Electronics'].map((dept) => (
              <button
                key={dept}
                type="button"
                className={`roadmap-filter-btn ${department === dept ? 'active' : ''}`}
                onClick={() => setDepartment(dept)}
              >
                {dept}
              </button>
            ))}
          </div>

          {/* Priority Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Triage Filter:</span>
            {['ALL', 'High', 'Medium', 'Low'].map((p) => (
              <button
                key={p}
                type="button"
                className={`roadmap-filter-btn ${priorityFilter === p ? 'active' : ''}`}
                onClick={() => setPriorityFilter(p)}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Roster Table */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
          Candidate Assessment & Intervention Roster ({filteredRoster.length} Candidates):
        </h3>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <span className="spinner" style={{ margin: '0 auto 1rem' }} />
            <p>Loading cohort assessment roster...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Department</th>
                  <th>CGPA</th>
                  <th>Comm (10)</th>
                  <th>Status</th>
                  <th>Confidence</th>
                  <th>Triage Priority</th>
                  <th>Intervention Reason</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRoster.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <strong>{r.name}</strong>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.email}</div>
                    </td>
                    <td>{r.department}</td>
                    <td><strong>{r.cgpa.toFixed(2)}</strong></td>
                    <td>{r.communication}</td>
                    <td>
                      <span className={`badge ${r.prediction_status === 'Placed' ? 'badge-success' : 'badge-danger'}`}>
                        {r.prediction_status}
                      </span>
                    </td>
                    <td>{Math.round(r.probability * 100)}%</td>
                    <td>
                      <span className={`badge ${r.priority_badge}`}>
                        {r.intervention_priority}
                      </span>
                    </td>
                    <td style={{ maxWidth: '240px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      {r.intervention_reason}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
                        onClick={() => {
                          setSelectedStudent(r);
                          setReason(r.intervention_reason);
                          setActionPlan('Enrolled in Week 3 behavioral communication workshop and scheduled 1-on-1 counselor interview.');
                        }}
                      >
                        + Record Action
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recorded Interventions Log */}
      {interventions.length > 0 && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
            📋 Counselor Logged Interventions ({interventions.length}):
          </h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Student</th>
                  <th>Priority</th>
                  <th>Remediation Trigger</th>
                  <th>Action Plan Assigned</th>
                  <th>Follow-up</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {interventions.map((inv) => (
                  <tr key={inv.id}>
                    <td>{inv.created_at ? new Date(inv.created_at).toLocaleDateString() : '—'}</td>
                    <td>
                      <strong>{inv.student_name}</strong>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{inv.student_email}</div>
                    </td>
                    <td>
                      <span className={`badge ${inv.priority === 'High' ? 'badge-danger' : 'badge-warning'}`}>
                        {inv.priority}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem' }}>{inv.reason}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>{inv.action_plan}</td>
                    <td>{inv.follow_up_date || 'Pending'}</td>
                    <td><span className="badge badge-success">{inv.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Intervention Modal */}
      {selectedStudent && (
        <div className="intervention-modal-overlay">
          <div className="intervention-modal animate-fade-in-up">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              Assign Mentor Intervention
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Candidate: <strong>{selectedStudent.name}</strong> ({selectedStudent.department})
            </p>

            <form onSubmit={handleSaveIntervention}>
              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label>Intervention Priority:</label>
                <select
                  value={selectedStudent.intervention_priority}
                  disabled
                  style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)' }}
                >
                  <option value={selectedStudent.intervention_priority}>{selectedStudent.intervention_priority}</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label>Identified Deficiency / Reason:</label>
                <textarea
                  className="resume-text-input"
                  style={{ height: '80px' }}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label>Target Remedial Action Plan:</label>
                <textarea
                  className="resume-text-input"
                  style={{ height: '90px' }}
                  value={actionPlan}
                  onChange={(e) => setActionPlan(e.target.value)}
                  placeholder="e.g. Mandatory attendance in DSA sprint, assigned peer mentor..."
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label>Follow-up Review Date:</label>
                <input
                  type="date"
                  value={followUpDate}
                  onChange={(e) => setFollowUpDate(e.target.value)}
                  style={{
                    padding: '0.6rem 0.8rem',
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                  }}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setSelectedStudent(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={savingIntervention}
                >
                  {savingIntervention ? 'Saving...' : 'Confirm Intervention'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
