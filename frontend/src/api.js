/**
 * Complete API service for the Career Intelligence & Placement Preparation Platform.
 * Communicates with the Flask REST API via Vite proxy or production BASE URL.
 */

const BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export function getAuthToken() {
  return localStorage.getItem('auth_token') || '';
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const headers = { ...options.headers };

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const apiKey = import.meta.env.VITE_API_KEY;
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }

  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const err = new Error(data.error || `Request failed with status ${res.status}`);
    err.status = res.status;
    err.details = data.details;
    throw err;
  }

  return { data, headers: res.headers };
}

// ---------------------------------------------------------------------------
// Health & Telemetry
// ---------------------------------------------------------------------------
export function getHealth() {
  return request('/health');
}

export function getReady() {
  return request('/ready');
}

export function getMetrics() {
  return request('/metrics');
}

export function getModelInfo() {
  return request('/model/info');
}

export function getModelMonitoring() {
  return request('/model/monitoring');
}

// ---------------------------------------------------------------------------
// Predictions & Explainability
// ---------------------------------------------------------------------------
export function predictSingle(payload, explain = true) {
  return request('/predict?explain=' + (explain ? 'true' : 'false'), {
    method: 'POST',
    body: JSON.stringify({ ...payload, explain }),
  });
}

export function predictBatch(items) {
  return request('/predict', {
    method: 'POST',
    body: JSON.stringify(items),
  });
}

export function explainPrediction(payload) {
  return request('/explain', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ---------------------------------------------------------------------------
// What-If Simulator
// ---------------------------------------------------------------------------
export function runSimulation(baseline, hypothetical) {
  return request('/simulator/simulate', {
    method: 'POST',
    body: JSON.stringify({ baseline, hypothetical }),
  });
}

// ---------------------------------------------------------------------------
// Career Improvement Roadmap
// ---------------------------------------------------------------------------
export function getRoadmap() {
  return request('/roadmap');
}

export function generateRoadmap(profile) {
  return request('/roadmap/generate', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export function updateRoadmapTask(taskId, status) {
  return request(`/roadmap/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

// ---------------------------------------------------------------------------
// Job Role Matching
// ---------------------------------------------------------------------------
export function getJobRoles() {
  return request('/roles');
}

export function matchJobRoles(profile, roleKey = null) {
  return request('/roles/match', {
    method: 'POST',
    body: JSON.stringify({ profile, role_key: roleKey }),
  });
}

// ---------------------------------------------------------------------------
// AI Career Mentor Chat
// ---------------------------------------------------------------------------
export function sendMentorMessage(message, studentContext = {}, history = []) {
  return request('/mentor/chat', {
    method: 'POST',
    body: JSON.stringify({ message, student_context: studentContext, history }),
  });
}

// ---------------------------------------------------------------------------
// Mock Assessments
// ---------------------------------------------------------------------------
export function getMockTests() {
  return request('/assessments/tests');
}

export function startMockTest(testType) {
  return request(`/assessments/tests/${testType}/start`);
}

export function submitMockTest(testType, answers, timeSpentSecs) {
  return request(`/assessments/tests/${testType}/submit`, {
    method: 'POST',
    body: JSON.stringify({ answers, time_spent_secs: timeSpentSecs }),
  });
}

// ---------------------------------------------------------------------------
// Resume Analyzer
// ---------------------------------------------------------------------------
export function analyzeResume(fileOrText) {
  if (typeof fileOrText === 'string') {
    return request('/resume/analyze', {
      method: 'POST',
      body: JSON.stringify({ resume_text: fileOrText }),
    });
  }

  const formData = new FormData();
  formData.append('file', fileOrText);
  return request('/resume/analyze', {
    method: 'POST',
    body: formData,
  });
}

export function matchResumeWithJD(resumeText, jobDescription) {
  return request('/resume/match-jd', {
    method: 'POST',
    body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
  });
}

// ---------------------------------------------------------------------------
// Mentor / TPO Early-Warning Dashboard
// ---------------------------------------------------------------------------
export function getTPOCohort(department = '') {
  const query = department ? `?department=${encodeURIComponent(department)}` : '';
  return request(`/tpo/cohort${query}`);
}

export function getTPOInterventions() {
  return request('/tpo/interventions');
}

export function recordTPOIntervention(interventionData) {
  return request('/tpo/interventions', {
    method: 'POST',
    body: JSON.stringify(interventionData),
  });
}

export function getTPOCSVExportUrl(department = '') {
  const query = department ? `?department=${encodeURIComponent(department)}` : '';
  return `${BASE}/tpo/export-csv${query}`;
}

// ---------------------------------------------------------------------------
// Authentication
// ---------------------------------------------------------------------------
export function loginUser(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export function registerUser(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser() {
  return request('/auth/me');
}
