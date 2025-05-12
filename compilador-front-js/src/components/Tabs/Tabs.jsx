import React from 'react';
import './Tabs.css';

export default function Tabs({ tabs, activeTabId, onSelect, onClose }) {
  return (
    <nav className="tabs">
      {tabs.map(tab => (
        <div
          key={tab.id}
          className={`tab-item ${tab.id === activeTabId ? 'active' : ''}`}
        >
          <span onClick={() => onSelect(tab.id)}>{tab.title}</span>
          <button
            className="tab-close-btn"
            onClick={() => tabs.length > 1 && onClose(tab.id)}
            disabled={tabs.length <= 1}
          >
            ×
          </button>
        </div>
      ))}
    </nav>
  );
}
