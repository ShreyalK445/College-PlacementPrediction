import { useState, useRef } from 'react';
import './ResumeAnalyzerView.css';
import { analyzeResume, matchResumeWithJD } from '../api';

const SAMPLE_RESUME = `Alex Morgan
Email: alex.morgan@college.edu | Phone: +1-555-019-2834
GitHub: github.com/alex-morgan | LinkedIn: linkedin.com/in/alex-morgan

EDUCATION
Bachelor of Technology in Computer Science & Engineering
GPA: 8.8 / 10.0 | Expected Graduation: 2026

TECHNICAL SKILLS
Languages: Python, Java, SQL, JavaScript, HTML, CSS
Frameworks & Libraries: React, Flask, Pandas, NumPy, Scikit-Learn
Tools & Platforms: Git, GitHub, Docker, Linux, REST APIs

PROJECTS
• College Placement Prediction System: Engineered an end-to-end ML prediction engine using Random Forest with 90.5% accuracy. Built responsive dark-theme glassmorphism UI with React 19 and Flask REST API.
• Distributed Task Queue: Developed an asynchronous job scheduler with Python Redis and Docker containerization.

WORK EXPERIENCE
Software Engineering Intern | TechNova Solutions
• Developed and deployed 4 production REST API microservices with input validation and rate limiting.
• Improved database query performance by 22% using optimized indexing.

CERTIFICATIONS
• DeepLearning.AI Machine Learning Specialization
• AWS Certified Cloud Practitioner`;

export default function ResumeAnalyzerView() {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const [resumeText, setResumeText] = useState(SAMPLE_RESUME);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // JD Matcher State
  const [jdText, setJdText] = useState('');
  const [jdResult, setJdResult] = useState(null);
  const [jdLoading, setJdLoading] = useState(false);
  const fileInputRef = useRef(null);

  async function handleAnalyze(e) {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    setJdResult(null);

    try {
      const payload = inputMode === 'file' ? selectedFile : resumeText;
      if (!payload) {
        throw new Error('Please select a PDF file or enter resume text.');
      }
      const res = await analyzeResume(payload);
      setAnalysis(res.data);
    } catch (err) {
      setError(err.message || 'Resume analysis failed.');
    } finally {
      setLoading(false);
    }
  }

  async function handleMatchJD(e) {
    e.preventDefault();
    if (!jdText.trim()) return;
    setJdLoading(true);

    try {
      const res = await matchResumeWithJD(resumeText, jdText);
      setJdResult(res.data);
    } catch (err) {
      setError(err.message || 'Job description matching failed.');
    } finally {
      setJdLoading(false);
    }
  }

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setAnalysis(null);
    }
  }

  return (
    <div className="resume-container animate-fade-in-up">
      {/* Header */}
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">📄</span>
          <div>
            <h2>Resume Analyzer & Job Description Matcher</h2>
            <p>Upload a PDF resume or inspect text credentials to audit keyword coverage and ATS alignment</p>
          </div>
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: '1.25rem' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Input Mode Tabs */}
        <div className="resume-input-tabs">
          <button
            type="button"
            className={`resume-input-tab ${inputMode === 'text' ? 'active' : ''}`}
            onClick={() => setInputMode('text')}
          >
            ✏️ Paste Plain Text
          </button>
          <button
            type="button"
            className={`resume-input-tab ${inputMode === 'file' ? 'active' : ''}`}
            onClick={() => setInputMode('file')}
          >
            📁 Upload PDF Resume
          </button>
        </div>

        {inputMode === 'text' ? (
          <div>
            <textarea
              className="resume-text-input"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your complete resume text here..."
            />
          </div>
        ) : (
          <div
            className="file-drop-zone"
            onClick={() => fileInputRef.current?.click()}
            style={{ padding: '2rem 1.5rem' }}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <div className="drop-icon">📑</div>
            <p>
              {selectedFile ? (
                <strong style={{ color: 'var(--accent-cyan)' }}>Selected: {selectedFile.name}</strong>
              ) : (
                'Click or drag & drop PDF resume here (Max 5MB)'
              )}
            </p>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" /> Analyzing Resume Credentials...
              </>
            ) : (
              <>🔍 Run Resume Audit</>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Output */}
      {analysis && (
        <div className="glass-card animate-fade-in-up">
          <div className="section-header" style={{ marginBottom: '1rem' }}>
            <span className="icon">📊</span>
            <div>
              <h2>Resume Strength Assessment</h2>
              <p>Word Count: {analysis.word_count} words • Parsed Structural Quality</p>
            </div>
          </div>

          {/* Strength Score Card */}
          <div className="sim-metric-card hypothetical" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
              Resume Structural Strength Score
            </span>
            <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
              {analysis.resume_strength_score} / 100
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Based on keyword density, contact availability, and key section presences.
            </p>
          </div>

          {/* Section Presence Checklist */}
          <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
            ATS Section Architecture Audit:
          </h4>
          <div className="checklist-grid">
            <div className="checklist-item">
              <span>{analysis.structural_checks.has_projects_section ? '✅' : '❌'}</span>
              <span>Projects / Capstones Section</span>
            </div>
            <div className="checklist-item">
              <span>{analysis.structural_checks.has_internship_section ? '✅' : '❌'}</span>
              <span>Work Experience / Internships</span>
            </div>
            <div className="checklist-item">
              <span>{analysis.structural_checks.has_education_section ? '✅' : '❌'}</span>
              <span>Education & Degree Details</span>
            </div>
            <div className="checklist-item">
              <span>{analysis.structural_checks.has_certifications_section ? '✅' : '❌'}</span>
              <span>Professional Certifications</span>
            </div>
          </div>

          {/* Detected Skills */}
          <div style={{ margin: '1.5rem 0' }}>
            <h4 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              Technical Keywords Identified ({analysis.technical_skills.length}):
            </h4>
            <div className="skills-wrap">
              {analysis.technical_skills.map((s) => (
                <span key={s} className="skill-pill matched">
                  ✓ {s}
                </span>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="insights-box">
            <h4>💡 Recommended Resume Upgrades</h4>
            <ul>
              {analysis.suggested_improvements.map((imp, idx) => (
                <li key={idx}>{imp}</li>
              ))}
            </ul>
          </div>

          {/* Target Job Description Matcher Sub-Section */}
          <div className="jd-matcher-box">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--accent-cyan)' }}>
              🎯 Target Job Description Matcher
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Paste a specific campus recruitment job description (JD) below to compute keyword alignment:
            </p>

            <textarea
              className="resume-text-input"
              style={{ height: '120px' }}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste Job Description requirements (e.g. Seeking Software Developer skilled in Python, SQL, Docker, React, AWS)..."
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.75rem' }}>
              <button
                type="button"
                className="btn btn-outline"
                onClick={handleMatchJD}
                disabled={jdLoading || !jdText.trim()}
              >
                {jdLoading ? <span className="spinner" /> : '⚡ Check JD Keyword Match'}
              </button>
            </div>

            {jdResult && (
              <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: 0 }}>
                    Alignment Score: <span style={{ color: 'var(--accent-cyan)', fontWeight: 800 }}>{jdResult.match_percentage}%</span>
                  </h4>
                  <span className={`badge ${jdResult.match_percentage >= 70 ? 'badge-success' : 'badge-warning'}`}>
                    {jdResult.match_percentage >= 70 ? 'High Alignment' : 'Gap Detected'}
                  </span>
                </div>

                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Matched Skills:</div>
                  <div className="skills-wrap">
                    {jdResult.matching_skills.map((s) => (
                      <span key={s} className="skill-pill matched">
                        ✓ {s}
                      </span>
                    ))}
                  </div>
                </div>

                {jdResult.missing_skills.length > 0 && (
                  <div style={{ marginBottom: '0.75rem' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Missing JD Keywords:</div>
                    <div className="skills-wrap">
                      {jdResult.missing_skills.map((s) => (
                        <span key={s} className="skill-pill missing">
                          ✕ {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
