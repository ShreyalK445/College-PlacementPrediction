import { useState, useEffect } from 'react';
import './MockInterviewView.css';
import { getMockTests, startMockTest, submitMockTest } from '../api';

export default function MockInterviewView() {
  const [catalog, setCatalog] = useState([]);
  const [activeTest, setActiveTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [scorecard, setScorecard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadCatalog() {
      try {
        setLoading(true);
        const res = await getMockTests();
        setCatalog(res.data.tests || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadCatalog();
  }, []);

  const submitRef = useRef(handleSubmitTest);
  useEffect(() => {
    submitRef.current = handleSubmitTest;
  });

  // Timer countdown
  useEffect(() => {
    if (!activeTest || scorecard || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(interval);
          submitRef.current?.();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [activeTest, scorecard, timeLeft]);

  async function handleStartTest(test) {
    try {
      setLoading(true);
      setError(null);
      const res = await startMockTest(test.test_type);
      setQuestions(res.data.questions || []);
      setActiveTest(test);
      setCurrentIdx(0);
      setAnswers({});
      setTimeLeft(test.time_limit_mins * 60);
      setScorecard(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSelectOption(questionId, optionIdx) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionIdx,
    }));
  }

  async function handleSubmitTest() {
    if (!activeTest) return;
    try {
      setLoading(true);
      setError(null);
      const totalTime = activeTest.time_limit_mins * 60;
      const timeSpent = Math.max(0, totalTime - timeLeft);
      const res = await submitMockTest(activeTest.test_type, answers, timeSpent);
      setScorecard(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  const currentQ = questions[currentIdx];

  return (
    <div className="mock-container animate-fade-in-up">
      {/* Header */}
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">📝</span>
          <div>
            <h2>Smart Mock Interview & Assessment Suite</h2>
            <p>Timed practice examinations with detailed rubric scorecards, topic breakdowns, and explanations</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* 1. Test Catalog View */}
      {!activeTest && (
        <div className="test-catalog-grid">
          {catalog.map((test) => (
            <div key={test.test_type} className="test-card">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '2rem' }}>{test.icon}</span>
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>{test.title}</h3>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      ⏱️ {test.time_limit_mins} Mins • ❓ {test.question_count} Questions
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
                  {test.description}
                </p>
              </div>

              <button
                type="button"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => handleStartTest(test)}
                disabled={loading}
              >
                Start Assessment ➔
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 2. Active Quiz Runner */}
      {activeTest && !scorecard && currentQ && (
        <div className="glass-card quiz-runner-card animate-fade-in-up">
          <div className="quiz-header-bar">
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{activeTest.title}</h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Question {currentIdx + 1} of {questions.length} • {currentQ.category}
              </span>
            </div>
            <div className="timer-pill">⏳ {formatTime(timeLeft)}</div>
          </div>

          {/* Navigator Dots */}
          <div className="question-nav-strip">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                type="button"
                className={`q-dot ${currentIdx === idx ? 'current' : ''} ${answers[q.id] !== undefined ? 'answered' : ''}`}
                onClick={() => setCurrentIdx(idx)}
              >
                {idx + 1}
              </button>
            ))}
          </div>

          {/* Question Text */}
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', margin: '1rem 0 0.5rem' }}>
            {currentQ.question}
          </div>

          {/* Options */}
          <div className="options-list">
            {currentQ.options.map((opt, optIdx) => {
              const isSelected = answers[currentQ.id] === optIdx;
              return (
                <div
                  key={optIdx}
                  className={`option-box ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelectOption(currentQ.id, optIdx)}
                >
                  <input
                    type="radio"
                    name={`q_${currentQ.id}`}
                    className="option-radio"
                    checked={isSelected}
                    onChange={() => handleSelectOption(currentQ.id, optIdx)}
                  />
                  <span>{opt}</span>
                </div>
              );
            })}
          </div>

          {/* Quiz Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
            <button
              type="button"
              className="btn btn-outline"
              disabled={currentIdx === 0}
              onClick={() => setCurrentIdx((i) => i - 1)}
            >
              ← Previous
            </button>

            {currentIdx < questions.length - 1 ? (
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => setCurrentIdx((i) => i + 1)}
              >
                Next →
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSubmitTest}
                disabled={loading}
              >
                Submit Examination ✔
              </button>
            )}
          </div>
        </div>
      )}

      {/* 3. Comprehensive Scorecard View */}
      {scorecard && (
        <div className="glass-card animate-fade-in-up">
          <div className="scorecard-hero">
            <span style={{ fontSize: '2.5rem' }}>{scorecard.passed ? '🏆' : '📈'}</span>
            <div className="scorecard-pct" style={{ color: scorecard.passed ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
              {scorecard.percentage}%
            </div>
            <h3 style={{ fontSize: '1.25rem' }}>{scorecard.overall_verdict}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Scored {scorecard.score} out of {scorecard.total_questions} questions correct.
            </p>
          </div>

          {/* Category Breakdown */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Category Competency Breakdown:</h4>
            <div className="metrics-grid">
              {Object.entries(scorecard.category_breakdown).map(([cat, stat]) => (
                <div key={cat} className="metric-tile">
                  <div className="metric-value">{stat.percentage}%</div>
                  <div className="metric-label">{cat}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Personalized Recommendations */}
          <div className="insights-box" style={{ marginBottom: '1.5rem' }}>
            <h4>📋 Personalized Action Items:</h4>
            <ul>
              {scorecard.recommendations.map((r, idx) => (
                <li key={idx}>{r}</li>
              ))}
            </ul>
          </div>

          {/* Itemized Review */}
          <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Detailed Answer Review & Explanations:</h4>
          <div>
            {scorecard.review.map((item, idx) => (
              <div key={item.id} className={`review-item ${item.is_correct ? 'correct' : 'incorrect'}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <strong>Q{idx + 1}: {item.question}</strong>
                  <span className={`badge ${item.is_correct ? 'badge-success' : 'badge-danger'}`}>
                    {item.is_correct ? 'Correct (+1)' : 'Incorrect (0)'}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  💡 <strong>Explanation:</strong> {item.explanation}
                </div>
              </div>
            ))}
          </div>

          <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => {
                setActiveTest(null);
                setScorecard(null);
              }}
            >
              ← Back to Assessment Catalog
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
