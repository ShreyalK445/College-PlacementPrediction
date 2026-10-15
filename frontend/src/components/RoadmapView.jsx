import { useState, useEffect } from 'react';
import './RoadmapView.css';
import { getRoadmap, generateRoadmap, updateRoadmapTask } from '../api';

export default function RoadmapView({ studentProfile }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeWeek, setActiveWeek] = useState('ALL');
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await getRoadmap();
        setTasks(res.data.tasks || []);
      } catch (err) {
        setError(err.message || 'Failed to load career roadmap.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleToggleStatus(taskId, currentStatus) {
    const nextStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: nextStatus } : t))
    );

    try {
      if (typeof taskId === 'number') {
        await updateRoadmapTask(taskId, nextStatus);
      }
    } catch {
      // Revert if API update fails
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: currentStatus } : t))
      );
    }
  }

  async function handleRegenerate() {
    try {
      setLoading(true);
      setError(null);
      const res = await generateRoadmap(studentProfile || { CGPA: 7.4, Communication_Skills: 7 });
      setTasks(res.data.tasks || []);
    } catch (err) {
      setError(err.message || 'Failed to regenerate roadmap.');
    } finally {
      setLoading(false);
    }
  }

  const completedCount = tasks.filter((t) => t.status === 'completed').length;
  const totalCount = tasks.length;
  const completionPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  const categories = ['ALL', ...new Set(tasks.map((t) => t.category))];

  const filteredTasks = tasks.filter((t) => {
    if (activeWeek !== 'ALL' && t.week_number !== Number(activeWeek)) return false;
    if (activeCategory !== 'ALL' && t.category !== activeCategory) return false;
    return true;
  });

  return (
    <div className="roadmap-container animate-fade-in-up">
      {/* Header & Milestone Progress */}
      <div className="glass-card roadmap-progress-card">
        <div className="roadmap-progress-info">
          <div className="section-header" style={{ marginBottom: '0.5rem' }}>
            <span className="icon">🗺️</span>
            <div>
              <h2>Personalized Career Roadmap</h2>
              <p>8-Week structured milestone plan tailored to your profile weaknesses and recruitment benchmarks</p>
            </div>
          </div>
          <div className="prob-meter-container" style={{ maxWidth: '400px', marginTop: '1rem' }}>
            <div className="prob-label-row">
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Roadmap Execution:</span>
              <span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                {completedCount} / {totalCount} Tasks Done ({completionPct}%)
              </span>
            </div>
            <div className="prob-track">
              <div
                className="prob-fill high"
                style={{ width: `${completionPct}%`, background: 'var(--gradient-primary)' }}
              />
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleRegenerate}
            disabled={loading}
          >
            🔄 Sync with Latest Assessment
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="glass-card" style={{ padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Week Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Filter by Week:</span>
            <button
              type="button"
              className={`roadmap-filter-btn ${activeWeek === 'ALL' ? 'active' : ''}`}
              onClick={() => setActiveWeek('ALL')}
            >
              All Weeks
            </button>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((w) => (
              <button
                key={w}
                type="button"
                className={`roadmap-filter-btn ${activeWeek === String(w) ? 'active' : ''}`}
                onClick={() => setActiveWeek(String(w))}
              >
                Week {w}
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Category:</span>
            {categories.map((c) => (
              <button
                key={c}
                type="button"
                className={`roadmap-filter-btn ${activeCategory === c ? 'active' : ''}`}
                onClick={() => setActiveCategory(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="task-list">
        {loading ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
            <span className="spinner" style={{ margin: '0 auto 1rem' }} />
            <p>Loading your developmental roadmap...</p>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="empty-state glass-card">
            <div className="empty-icon">📭</div>
            <p>No roadmap tasks found for the selected filter.</p>
          </div>
        ) : (
          filteredTasks.map((t) => {
            const isDone = t.status === 'completed';
            return (
              <div
                key={t.id || t.title}
                className={`task-card ${isDone ? 'completed' : ''}`}
              >
                <div className="task-checkbox-wrap">
                  <input
                    type="checkbox"
                    className="task-checkbox"
                    checked={isDone}
                    onChange={() => handleToggleStatus(t.id, t.status)}
                  />
                </div>

                <div className="task-content">
                  <div className="task-top-meta">
                    <span className="week-tag">Week {t.week_number}</span>
                    <span className="category-tag">{t.category}</span>
                    <span
                      className={`badge ${
                        t.priority === 'High'
                          ? 'badge-danger'
                          : t.priority === 'Medium'
                          ? 'badge-warning'
                          : 'badge-success'
                      }`}
                    >
                      {t.priority} Priority
                    </span>
                    {t.deadline && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                        ⏰ Target: {t.deadline}
                      </span>
                    )}
                  </div>

                  <h3 className={`task-title ${isDone ? 'strikethrough' : ''}`}>{t.title}</h3>
                  <p className="task-desc">{t.description}</p>

                  {t.relevance_reason && (
                    <div className="task-relevance">
                      <strong>Target Benefit:</strong> {t.relevance_reason}
                    </div>
                  )}

                  {t.resources?.length > 0 && (
                    <div className="resource-pills">
                      {t.resources.map((r, idx) => (
                        <a
                          key={idx}
                          href={r.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="resource-link"
                        >
                          🔗 {r.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        * Disclaimer: Roadmap completion strengthens placement competencies. It does not promise guaranteed hiring or specific salary figures.
      </div>
    </div>
  );
}
