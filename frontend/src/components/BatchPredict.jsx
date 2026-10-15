import { useState, useRef } from 'react';
import './BatchPredict.css';
import { predictBatch } from '../api';

const SAMPLE_CSV = `IQ,Prev_Sem_Result,CGPA,Academic_Performance,Extra_Curricular_Score,Communication_Skills,Projects_Completed,Internship_Experience
120,8.2,8.4,9,8,8,3,1
102,6.8,7.1,6,5,6,2,0
135,9.1,9.3,10,9,9,5,1
94,5.4,5.7,5,4,5,1,0
115,7.9,8.0,8,7,8,3,1
108,7.3,7.4,7,6,7,2,1
88,5.1,5.2,4,3,4,0,0
128,8.8,8.9,9,8,9,4,1
112,7.6,7.8,7,7,7,3,0
99,6.2,6.5,6,5,6,1,0`;

const DEMO_STUDENTS = [
  { IQ: 120, Prev_Sem_Result: 8.2, CGPA: 8.4, Academic_Performance: 9, Extra_Curricular_Score: 8, Communication_Skills: 8, Projects_Completed: 3, Internship_Experience: 1 },
  { IQ: 102, Prev_Sem_Result: 6.8, CGPA: 7.1, Academic_Performance: 6, Extra_Curricular_Score: 5, Communication_Skills: 6, Projects_Completed: 2, Internship_Experience: 0 },
  { IQ: 135, Prev_Sem_Result: 9.1, CGPA: 9.3, Academic_Performance: 10, Extra_Curricular_Score: 9, Communication_Skills: 9, Projects_Completed: 5, Internship_Experience: 1 },
  { IQ: 94, Prev_Sem_Result: 5.4, CGPA: 5.7, Academic_Performance: 5, Extra_Curricular_Score: 4, Communication_Skills: 5, Projects_Completed: 1, Internship_Experience: 0 },
  { IQ: 115, Prev_Sem_Result: 7.9, CGPA: 8.0, Academic_Performance: 8, Extra_Curricular_Score: 7, Communication_Skills: 8, Projects_Completed: 3, Internship_Experience: 1 },
  { IQ: 108, Prev_Sem_Result: 7.3, CGPA: 7.4, Academic_Performance: 7, Extra_Curricular_Score: 6, Communication_Skills: 7, Projects_Completed: 2, Internship_Experience: 1 },
  { IQ: 88, Prev_Sem_Result: 5.1, CGPA: 5.2, Academic_Performance: 4, Extra_Curricular_Score: 3, Communication_Skills: 4, Projects_Completed: 0, Internship_Experience: 0 },
  { IQ: 128, Prev_Sem_Result: 8.8, CGPA: 8.9, Academic_Performance: 9, Extra_Curricular_Score: 8, Communication_Skills: 9, Projects_Completed: 4, Internship_Experience: 1 },
  { IQ: 112, Prev_Sem_Result: 7.6, CGPA: 7.8, Academic_Performance: 7, Extra_Curricular_Score: 7, Communication_Skills: 7, Projects_Completed: 3, Internship_Experience: 0 },
  { IQ: 99, Prev_Sem_Result: 6.2, CGPA: 6.5, Academic_Performance: 6, Extra_Curricular_Score: 5, Communication_Skills: 6, Projects_Completed: 1, Internship_Experience: 0 },
];

export default function BatchPredict({ onResults }) {
  const [itemsToPredict, setItemsToPredict] = useState([]);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [filter, setFilter] = useState('ALL');
  const fileInputRef = useRef(null);

  function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/).filter(line => line.trim().length > 0);
    if (lines.length < 2) {
      throw new Error('CSV must contain a header row and at least one student data row');
    }

    const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
    const expected = [
      'IQ',
      'Prev_Sem_Result',
      'CGPA',
      'Academic_Performance',
      'Extra_Curricular_Score',
      'Communication_Skills',
      'Projects_Completed',
      'Internship_Experience'
    ];

    const missing = expected.filter(exp => !headers.includes(exp));
    if (missing.length > 0) {
      throw new Error(`CSV missing required columns: ${missing.join(', ')}`);
    }

    const parsed = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      if (values.length !== headers.length) continue;

      const rowObj = {};
      headers.forEach((h, idx) => {
        rowObj[h] = parseFloat(values[idx]);
      });
      parsed.push(rowObj);
    }

    return parsed;
  }

  function handleFileSelect(file) {
    if (!file) return;
    setFileName(file.name);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const parsed = parseCSV(text);
        setItemsToPredict(parsed);
      } catch (err) {
        setError(err.message);
        setItemsToPredict([]);
      }
    };
    reader.readAsText(file);
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }

  function loadDemo() {
    setFileName('demo_placement_cohort.csv');
    setItemsToPredict(DEMO_STUDENTS);
    setError(null);
  }

  function downloadTemplate() {
    const blob = new Blob([SAMPLE_CSV], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'placement_batch_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function executeBatch() {
    if (itemsToPredict.length === 0) return;
    setLoading(true);
    setError(null);

    try {
      const response = await predictBatch(itemsToPredict);
      const outputList = Array.isArray(response.data.results)
        ? response.data.results
        : [response.data.results];

      const combined = itemsToPredict.map((input, idx) => {
        const res = outputList[idx] || {};
        return {
          id: Date.now() + '-' + idx,
          timestamp: new Date().toISOString(),
          inputs: input,
          prediction: res.placement_prediction,
          status: res.status || (res.placement_prediction === 1 ? 'Placed' : 'Not Placed'),
          probability: res.placement_probability ?? (res.placement_prediction === 1 ? 0.85 : 0.25),
        };
      });

      setResults(combined);
      if (onResults) {
        onResults(combined);
      }
    } catch (err) {
      setError(err.message || 'Batch prediction failed. Ensure backend service is reachable.');
    } finally {
      setLoading(false);
    }
  }

  function exportResultsCSV() {
    if (!results || results.length === 0) return;
    const headers = [
      'Candidate_ID',
      'IQ',
      'Prev_Sem_Result',
      'CGPA',
      'Academic_Performance',
      'Extra_Curricular_Score',
      'Communication_Skills',
      'Projects_Completed',
      'Internship_Experience',
      'Prediction_Result',
      'Status',
      'Placement_Probability'
    ];

    const rows = results.map((r, i) => [
      i + 1,
      r.inputs.IQ,
      r.inputs.Prev_Sem_Result,
      r.inputs.CGPA,
      r.inputs.Academic_Performance,
      r.inputs.Extra_Curricular_Score,
      r.inputs.Communication_Skills,
      r.inputs.Projects_Completed,
      r.inputs.Internship_Experience,
      r.prediction,
      r.status,
      (r.probability * 100).toFixed(1) + '%'
    ]);

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `placement_batch_results_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const placedCount = results ? results.filter(r => r.prediction === 1).length : 0;
  const notPlacedCount = results ? results.length - placedCount : 0;
  const placementRate = results && results.length > 0
    ? ((placedCount / results.length) * 100).toFixed(1)
    : 0;

  const filteredResults = results
    ? results.filter(r => {
        if (filter === 'PLACED') return r.prediction === 1;
        if (filter === 'NOT_PLACED') return r.prediction === 0;
        return true;
      })
    : [];

  return (
    <div className="batch-container animate-fade-in-up">
      <div className="glass-card">
        <div className="section-header">
          <span className="icon">📦</span>
          <div>
            <h2>Batch Cohort Analysis</h2>
            <p>Upload a class cohort CSV to process high-throughput placement evaluations in one pass</p>
          </div>
        </div>

        {error && (
          <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="batch-upload-grid">
          {/* Dropzone */}
          <div
            className={`file-drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />
            <div className="drop-icon">📁</div>
            <p>
              {fileName ? (
                <strong style={{ color: 'var(--accent-cyan)' }}>Selected: {fileName} ({itemsToPredict.length} records)</strong>
              ) : (
                'Drag & drop student CSV file here, or click to browse'
              )}
            </p>
            <p className="hint">Supports UTF-8 CSV with valid feature headers</p>
          </div>

          {/* Quick Actions & Template */}
          <div className="batch-instructions">
            <div className="template-box">
              <h4>📋 Standard Schema</h4>
              <p>Columns required: IQ, Prev_Sem_Result, CGPA, Academic_Performance, Extra_Curricular_Score, Communication_Skills, Projects_Completed, Internship_Experience</p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <button type="button" className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={downloadTemplate}>
                  ⬇️ Download Template
                </button>
                <button type="button" className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={loadDemo}>
                  ⚡ Load 10 Demo Students
                </button>
              </div>
            </div>

            {itemsToPredict.length > 0 && (
              <button
                type="button"
                className="btn btn-primary"
                style={{ width: '100%' }}
                disabled={loading}
                onClick={executeBatch}
              >
                {loading ? (
                  <>
                    <span className="spinner" /> Analyzing {itemsToPredict.length} Candidates...
                  </>
                ) : (
                  <>🚀 Predict All ({itemsToPredict.length} Students)</>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Batch Results Output */}
      {results && (
        <div className="glass-card animate-fade-in-up">
          <div className="section-header" style={{ marginBottom: '1rem' }}>
            <span className="icon">📊</span>
            <div>
              <h2>Cohort Assessment Summary</h2>
              <p>Batch inference completed across {results.length} student records</p>
            </div>
          </div>

          {/* Summary Metric Tiles */}
          <div className="batch-summary-cards" style={{ marginBottom: '1.5rem' }}>
            <div className="metric-tile">
              <div className="metric-value">{results.length}</div>
              <div className="metric-label">Total Evaluated</div>
            </div>
            <div className="metric-tile">
              <div className="metric-value" style={{ color: 'var(--accent-emerald)' }}>
                {placedCount}
              </div>
              <div className="metric-label">Predicted Placed</div>
            </div>
            <div className="metric-tile">
              <div className="metric-value" style={{ color: 'var(--accent-rose)' }}>
                {notPlacedCount}
              </div>
              <div className="metric-label">Need Intervention</div>
            </div>
            <div className="metric-tile">
              <div className="metric-value">{placementRate}%</div>
              <div className="metric-label">Placement Rate</div>
            </div>
          </div>

          {/* Table Controls */}
          <div className="batch-controls">
            <div className="filter-pills">
              <button
                type="button"
                className={`filter-pill ${filter === 'ALL' ? 'active' : ''}`}
                onClick={() => setFilter('ALL')}
              >
                All ({results.length})
              </button>
              <button
                type="button"
                className={`filter-pill ${filter === 'PLACED' ? 'active' : ''}`}
                onClick={() => setFilter('PLACED')}
              >
                Placed ({placedCount})
              </button>
              <button
                type="button"
                className={`filter-pill ${filter === 'NOT_PLACED' ? 'active' : ''}`}
                onClick={() => setFilter('NOT_PLACED')}
              >
                Not Placed ({notPlacedCount})
              </button>
            </div>

            <button type="button" className="btn btn-outline" onClick={exportResultsCSV}>
              📥 Export Results (.csv)
            </button>
          </div>

          {/* Results Table */}
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>IQ</th>
                  <th>CGPA</th>
                  <th>Prev Sem</th>
                  <th>Acad (10)</th>
                  <th>Comm (10)</th>
                  <th>Projects</th>
                  <th>Internship</th>
                  <th>Status</th>
                  <th>Probability</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((r, idx) => (
                  <tr key={r.id}>
                    <td>{idx + 1}</td>
                    <td>{r.inputs.IQ}</td>
                    <td><strong>{Number(r.inputs.CGPA).toFixed(2)}</strong></td>
                    <td>{Number(r.inputs.Prev_Sem_Result).toFixed(2)}</td>
                    <td>{r.inputs.Academic_Performance}</td>
                    <td>{r.inputs.Communication_Skills}</td>
                    <td>{r.inputs.Projects_Completed}</td>
                    <td>{r.inputs.Internship_Experience === 1 ? 'Yes' : 'No'}</td>
                    <td>
                      <span className={`badge ${r.prediction === 1 ? 'badge-success' : 'badge-danger'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: r.prediction === 1 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                        {(r.probability * 100).toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
