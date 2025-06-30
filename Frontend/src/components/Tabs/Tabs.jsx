import React from 'react';
import './Tabs.css';
import useStore from '../../store/useStore';

export default function Tabs() {
  const { tabs, activeTabId, setActiveTabId, removeTab } = useStore();
  return (
    <nav className="tabs">
      {tabs.map(tab => (
        <div
          key={tab.id}
          className={`tab-item ${tab.id === activeTabId ? 'active' : ''}`}
        >
          <span onClick={() => setActiveTabId(tab.id)}>{tab.title}</span>
          <button
            className="tab-close-btn"
            onClick={() => tabs.length > 1 && removeTab(tab.id)}
            disabled={tabs.length <= 1}
          >
            ×
          </button>
        </div>
      ))}
    </nav>
  );
}
