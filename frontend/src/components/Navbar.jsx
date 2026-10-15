import './Navbar.css';

export default function Navbar({ tabs, activeTab, onTabChange, apiStatus }) {
  const statusColor =
    apiStatus === 'online' ? 'var(--accent-emerald)' :
    apiStatus === 'offline' ? 'var(--accent-rose)' :
    'var(--accent-amber)';

  const statusLabel =
    apiStatus === 'online' ? 'API Online' :
    apiStatus === 'offline' ? 'API Offline' :
    'Checking...';

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <span className="brand-icon">🎓</span>
          <div>
            <h1 className="brand-title">PlacePredict</h1>
            <span className="brand-sub">ML Prediction Engine</span>
          </div>
        </div>

        <div className="navbar-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => onTabChange(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="navbar-status">
          <span
            className="status-dot"
            style={{ background: statusColor, boxShadow: `0 0 8px ${statusColor}` }}
          />
          <span className="status-text">{statusLabel}</span>
        </div>
      </div>
    </nav>
  );
}
