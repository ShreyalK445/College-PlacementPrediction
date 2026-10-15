import { useState, useEffect } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import PredictionForm from './components/PredictionForm';
import WhatIfSimulator from './components/WhatIfSimulator';
import RoadmapView from './components/RoadmapView';
import JobRolesView from './components/JobRolesView';
import MentorChatView from './components/MentorChatView';
import MockInterviewView from './components/MockInterviewView';
import ResumeAnalyzerView from './components/ResumeAnalyzerView';
import TPODashboardView from './components/TPODashboardView';
import BatchPredict from './components/BatchPredict';
import History from './components/History';
import { getModelInfo, getHealth } from './api';

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'predict', label: 'Assess Profile', icon: '🔮' },
  { id: 'simulator', label: 'Simulator', icon: '🧪' },
  { id: 'roadmap', label: 'Roadmap', icon: '🗺️' },
  { id: 'roles', label: 'Job Roles', icon: '🎯' },
  { id: 'mentor', label: 'AI Mentor', icon: '🤖' },
  { id: 'assessments', label: 'Mock Tests', icon: '📝' },
  { id: 'resume', label: 'Resume', icon: '📄' },
  { id: 'tpo', label: 'TPO Portal', icon: '🏛️' },
  { id: 'batch', label: 'Batch CSV', icon: '📦' },
  { id: 'history', label: 'History', icon: '📜' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('predict');
  const [modelInfo, setModelInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [studentProfile, setStudentProfile] = useState({
    IQ: 110,
    Prev_Sem_Result: 7.5,
    CGPA: 7.6,
    Academic_Performance: 7,
    Extra_Curricular_Score: 6,
    Communication_Skills: 7,
    Projects_Completed: 2,
    Internship_Experience: 1,
  });

  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('prediction_history') || '[]');
    } catch {
      return [];
    }
  });

  // Persist history to localStorage
  useEffect(() => {
    localStorage.setItem('prediction_history', JSON.stringify(history));
  }, [history]);

  // Check API health & load model info on mount
  useEffect(() => {
    async function init() {
      try {
        await getHealth();
        setApiStatus('online');
      } catch {
        setApiStatus('offline');
      }

      try {
        const { data } = await getModelInfo();
        setModelInfo(data);
      } catch {
        // Model info fallback
      }
    }
    init();
  }, []);

  function addToHistory(record) {
    setHistory((prev) => [record, ...prev].slice(0, 100));
    if (record.inputs) {
      setStudentProfile(record.inputs);
    }
  }

  function clearHistory() {
    setHistory([]);
  }

  function handleNavigate(targetTab, profileData) {
    if (profileData) {
      setStudentProfile(profileData);
    }
    setActiveTab(targetTab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  return (
    <>
      <Navbar
        tabs={TABS}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        apiStatus={apiStatus}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard modelInfo={modelInfo} apiStatus={apiStatus} history={history} />
        )}
        {activeTab === 'predict' && (
          <PredictionForm
            modelInfo={modelInfo}
            onResult={addToHistory}
            onNavigate={handleNavigate}
          />
        )}
        {activeTab === 'simulator' && (
          <WhatIfSimulator
            initialProfile={studentProfile}
            onGenerateRoadmap={(hypo) => handleNavigate('roadmap', hypo)}
          />
        )}
        {activeTab === 'roadmap' && (
          <RoadmapView studentProfile={studentProfile} />
        )}
        {activeTab === 'roles' && (
          <JobRolesView studentProfile={studentProfile} />
        )}
        {activeTab === 'mentor' && (
          <MentorChatView studentProfile={studentProfile} />
        )}
        {activeTab === 'assessments' && (
          <MockInterviewView />
        )}
        {activeTab === 'resume' && (
          <ResumeAnalyzerView />
        )}
        {activeTab === 'tpo' && (
          <TPODashboardView />
        )}
        {activeTab === 'batch' && (
          <BatchPredict onResults={(records) => records.forEach(addToHistory)} />
        )}
        {activeTab === 'history' && (
          <History history={history} onClear={clearHistory} />
        )}
      </main>

      <footer className="app-footer">
        <p>
          AI-Powered Student Career Intelligence & Placement Preparation Platform v2.0 Enterprise
          <br />
          React 19 • Flask • Random Forest • Tree-Path Explainable AI
        </p>
      </footer>
    </>
  );
}
