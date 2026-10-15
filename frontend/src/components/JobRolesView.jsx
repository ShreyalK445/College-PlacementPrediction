import { useState, useEffect } from 'react';
import './JobRolesView.css';
import { matchJobRoles } from '../api';

const DEFAULT_SKILLS = [
  'Python',
  'Data Structures & Algorithms',
  'SQL & Relational Databases',
  'Git & Version Control',
  'REST APIs',
  'HTML',
  'CSS',
];

export default function JobRolesView({ studentProfile }) {
  const [skills, setSkills] = useState(DEFAULT_SKILLS);
  const [newSkill, setNewSkill] = useState('');
  const [roleMatches, setRoleMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function evaluate() {
      try {
        setLoading(true);
        const profile = {
          ...(studentProfile || { CGPA: 7.5, Communication_Skills: 7, Projects_Completed: 2 }),
          skills,
        };
        const res = await matchJobRoles(profile);
        setRoleMatches(res.data.matches || []);
      } catch (err) {
        setError(err.message || 'Failed to evaluate job roles.');
      } finally {
        setLoading(false);
      }
    }
    evaluate();
  }, [skills, studentProfile]);

  function addSkill(e) {
    e.preventDefault();
    const trimmed = newSkill.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills([...skills, trimmed]);
      setNewSkill('');
    }
  }

  function removeSkill(skillToRemove) {
    setSkills(skills.filter((s) => s !== skillToRemove));
  }

  return (
    <div className="roles-container animate-fade-in-up">
      {/* Header */}
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">🎯</span>
          <div>
            <h2>Job Role & Skill Gap Analysis</h2>
            <p>Benchmarking your credentials against 5 core campus recruitment technical profiles</p>
          </div>
        </div>

        {/* Skill Manager */}
        <div style={{ marginTop: '1rem' }}>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Your Declared Technical & Professional Skills:
          </h4>
          <div className="skills-input-bar">
            {skills.map((s) => (
              <span key={s} className="skill-tag">
                {s}
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeSkill(s)}
                >
                  ×
                </button>
              </span>
            ))}

            <form onSubmit={addSkill} style={{ display: 'inline-flex', gap: '0.4rem', marginLeft: 'auto' }}>
              <input
                type="text"
                placeholder="Add skill (e.g. Docker, Power BI)..."
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-glass)',
                  padding: '0.35rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                }}
              />
              <button type="submit" className="btn btn-outline" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                + Add
              </button>
            </form>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Role Cards Grid */}
      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <span className="spinner" style={{ margin: '0 auto 1rem' }} />
          <p>Analyzing skill matching across roles...</p>
        </div>
      ) : (
        <div className="roles-grid">
          {roleMatches.map((role) => (
            <div key={role.role_key} className="role-card">
              <div>
                <div className="role-header">
                  <div className="role-title-row">
                    <span style={{ fontSize: '2rem' }}>{role.icon}</span>
                    <div>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{role.title}</h3>
                      <span className={`badge ${role.cgpa_eligible ? 'badge-success' : 'badge-danger'}`} style={{ marginTop: '0.2rem' }}>
                        {role.cgpa_eligible ? '✓ CGPA Eligible' : `Min CGPA: ${role.min_cgpa}`}
                      </span>
                    </div>
                  </div>

                  <div>
                    <div className="role-score-circle">{role.readiness_score}%</div>
                    <div className="role-score-sub">Role Match</div>
                  </div>
                </div>

                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {role.description}
                </p>

                {/* Core Skills Match */}
                <div className="skill-section">
                  <h5>Core Competencies:</h5>
                  <div className="skills-wrap">
                    {role.matched_core_skills.map((s) => (
                      <span key={s} className="skill-pill matched">
                        ✓ {s}
                      </span>
                    ))}
                    {role.missing_core_skills.map((s) => (
                      <span key={s} className="skill-pill missing">
                        ✕ Missing: {s}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Recommended Certifications */}
                {role.recommended_certifications?.length > 0 && (
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                    <strong style={{ color: 'var(--accent-cyan)' }}>Certifications:</strong> {role.recommended_certifications.join(', ')}
                  </div>
                )}
              </div>

              {/* Actionable Study Plan */}
              {role.actionable_study_plan?.length > 0 && (
                <div className="role-study-plan">
                  <strong>Recommended Next Steps:</strong>
                  <ul>
                    {role.actionable_study_plan.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        * Role Readiness Score reflects skill and course alignment with target domains; it does not represent an external employer hiring guarantee.
      </div>
    </div>
  );
}
