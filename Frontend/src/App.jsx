import React, { useRef, useEffect } from 'react';
import './App.css';

import MenuBar from './components/MenuBar/MenuBar';
import Tabs from './components/Tabs/Tabs';
import Panel from './components/Panel/Panel';
import Editor from './components/Editor/Editor';
import Table from './components/Table/Table/Table';
import CsvTable from './components/Table/CsvTable/CsvTable';
import Popup from './components/Pop-up/Pop-up';
import useStore from './store/useStore';
import MepaEditor from './components/Mepa/Mepa';

export default function App() {
  const {
    panelVisible,
    setPanelVisible,
    panelHeight,
    setPanelHeight,
    tabs,
    activeTabId,
    table,
    csvText,
    isLoading,
    isPopupOpen,
    handleRunClick,
    setIsPopupOpen,
    resizing,
    startResize, // Adicionado do store
    setResizing, // Adicionado do store
    setCsvText, // Adicionado para o useEffect
    setIsLoading,
    handleInterpreterMepa
  } = useStore();

  const fileInputRef = useRef(null);

  // Corrigido: usando estado global de resizing
  useEffect(() => {
    const onMouseMove = e => {
      if (!resizing) return;
      const newHeight = window.innerHeight - e.clientY;
      setPanelHeight(Math.max(100, newHeight));
    };

    const onMouseUp = () => setResizing(false);
    
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [resizing, setResizing, setPanelHeight]);

  const activeTab = tabs.find(t => t.id === activeTabId);

  useEffect(() => {
    if (activeTab && activeTab.type === 'CsvTable') {
      setIsLoading(true);
      fetch('http://localhost:5000/tabela/'+activeTab.title)
        .then(res => {
          if (!res.ok) throw new Error(`Status ${res.status}`);
          return res.json();
        })
        .then(text => {
          setCsvText(text.tabela);
          setIsLoading(false);
        })
        .catch(err => {
          console.error('Erro ao buscar CSV:', err);
          setCsvText('');
          setIsLoading(false);
        });
    }
  }, [activeTab, setIsLoading, setCsvText]);

  return (
    <div className="app-container">
      <input
        type="file"
        accept=".txt"
        ref={fileInputRef}
        style={{ display: 'none' }}
      />
      <MenuBar />
      <Tabs />
      
      <main className="content">
        {activeTab && activeTab.type === 'editor' && (
          <div style={{ position: 'relative', height: '100%' }}>
            <Editor />
            <button className="run-button" onClick={handleRunClick}>▶</button>
          </div>
        )}
        {activeTab && activeTab.type === 'table' && (
          <Table type={activeTab.title} tableData={table} />
        )}
        {activeTab && activeTab.type === 'symbolTable' && (
          <Table type="TabelaSimbolos" tableData={activeTab.tableData} />
        )}
        {activeTab && activeTab.type === 'CsvTable' && (
          <CsvTable type={activeTab.title} tabela={csvText} />
        )}
        {activeTab && activeTab.type === 'mepa' && (
          <div style={{ position: 'relative', height: '100%' }}>
            <MepaEditor />
            <button 
              className="run-button" 
              onClick={handleInterpreterMepa}
              style={{ position: 'absolute', bottom: '10px', right: '10px', zIndex: 100 }}
            >
              ▶
            </button>
          </div>
        )}
        {activeTab && activeTab.type === 'interpretationResult' && (
          <div className="interpretation-result">
            <h3>Resultado da Interpretação MEPA</h3>
            
            <div className="result-section">
              <h4>Memória</h4>
              <pre>{JSON.stringify(activeTab.content.memoria, null, 2)}</pre>
            </div>
            
            <div className="result-section">
              <h4>Pilha (Topo: {activeTab.content.pilha})</h4>
              <pre>{JSON.stringify(activeTab.content.memoria.slice(0, activeTab.content.pilha + 1), null, 2)}</pre>
            </div>
            
            <div className="result-section">
              <h4>Saída</h4>
              <pre>{activeTab.content.saida.join('\n')}</pre>
            </div>
          </div>
        )}
      </main>
            
      {/* Adicione esta barra de resize */}
      {isLoading ? (
        <div className="loading-indicator">Carregando...</div>
      ) : (
        panelVisible && <Panel />
      )}
      
      <button
        className="toggle-panel-btn"
        onClick={() => setPanelVisible(!panelVisible)}
      >
        {panelVisible ? 'Ocultar Painel' : 'Mostrar Painel'}
      </button>
    
      
      <Popup isOpen={isPopupOpen} onClose={() => setIsPopupOpen(false)}>
        <p>Antes de executar o compilador escreva um programa em linguagem LALG.</p>
      </Popup>
    </div>
  );
}