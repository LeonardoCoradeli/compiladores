import React, { useState, useRef, useEffect } from 'react';
import './App.css';

import MenuBar from './components/MenuBar/MenuBar';
import Tabs from './components/Tabs/Tabs';
import Panel from './components/Panel/Panel';
import Editor from './components/Editor/Editor';
import Table from './components/Table/Table/Table';
import CsvTable from './components/Table/CsvTable/CsvTable';
import Popup from './components/Pop-up/Pop-up';

let nextTabId = 1;

export default function App() {
  const [menus, setMenus] = useState({ Arquivos: false, Tabelas: false });
  const [showDeclVars, setShowDeclVars] = useState(false);
  const [panelVisible, setPanelVisible] = useState(false);
  const [panelHeight, setPanelHeight] = useState(200);
  const [tabs, setTabs] = useState([
    { id: nextTabId++, title: 'Editor 1', type: 'editor', content: '' }
  ]);
  const [activeTabId, setActiveTabId] = useState(tabs[0].id);
  const [table, setTable] = useState(null);
  const [sintatico, setSintatico] = useState(null);
  const [csvText, setCsvText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState([]);
  const [isPopupOpen, setIsPopupOpen] = useState(false);

  const fileInputRef = useRef(null);
  const resizing = useRef(false);

  useEffect(() => {
    const onMouseMove = e => {
      if (!resizing.current) return;
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight > 50 && newHeight < window.innerHeight - 50) {
        setPanelHeight(newHeight);
      }
    };
    const onMouseUp = () => { resizing.current = false; };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);

  const activeTab = tabs.find(t => t.id === activeTabId);

  const saveFile = tabId => {
    const tab = tabs.find(t => t.id === tabId);
    if (!tab || tab.type !== 'editor') return;
    const blob = new Blob([tab.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${tab.title}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const removeTab = id => {
    if (tabs.length <= 1) return;
    setTabs(ts => ts.filter(t => t.id !== id));
    if (activeTabId === id) {
      const remaining = tabs.filter(t => t.id !== id);
      setActiveTabId(remaining[0].id);
    }
  };

  const addTab = ({ title, type, content = '' }) => {
    const id = nextTabId++;
    setTabs(ts => [...ts, { id, title, type, content }]);
    setActiveTabId(id);
  };

  const updateTabContent = (id, content) => {
    setTabs(ts => ts.map(t => t.id === id ? { ...t, content } : t));
  };

  const handleMenuAction = action => {
    switch (action) {
      case 'Salvar arquivo':
        saveFile(activeTabId);
        break;
      case 'Carregar arquivo':
        fileInputRef.current.click();
        break;
      case 'Novo Arquivo': {
        const replace = window.confirm(
          'Substituir o conteúdo da aba atual?\nClique em Cancelar para criar nova aba em branco.'
        );
        if (replace && activeTab.type === 'editor') {
          updateTabContent(activeTabId, '');
        } else {
          addTab({ title: `Editor ${nextTabId}`, type: 'editor' });
        }
        break;
      }
      case 'Lexico':
      case 'Léxicos':
        if(!table){
          setIsPopupOpen(true);
        }else{
          addTab({ title: 'Tabela Léxicos', type: 'table' });
        }
        break;
      case 'Programa':
        addTab({ title: 'Programa', type: 'CsvTable', tableId: 'Programa' });
        break;
      case 'Comandos':
        addTab({ title: 'Comandos', type: 'CsvTable', tableId: 'Comandos' });
        break;
      case 'Expressoes':
        addTab({ title: 'Expressoes', type: 'CsvTable', tableId: 'Expressoes' });
        break;
      case 'Completo':
        addTab({ title: 'Completa', type: 'CsvTable', tableId: 'Completo' });
        break;
      default:
        console.log(`Ação de menu não tratada: ${action}`);
    }
  };

  const handleFileChange = e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = evt => {
      const text = evt.target.result;
      const replace = window.confirm(
        'Substituir o conteúdo da aba atual?\nClique em Cancelar para criar nova aba com o arquivo.'
      );
      if (replace && activeTab.type === 'editor') {
        updateTabContent(activeTabId, text);
      } else {
        addTab({ title: file.name.replace(/\.txt$/, ''), type: 'editor', content: text });
      }
      e.target.value = null;
    };
    reader.readAsText(file);
  };

  const handleMenuToggle = menu => {
    setMenus(m => ({ ...m, [menu]: !m[menu] }));
    if (menu === 'Tabelas' && menus.Tabelas) setShowDeclVars(false);
    console.log(menus);
  };

  const startResize = () => {
    resizing.current = true;
    if (!panelVisible) setPanelVisible(true);
  };

  const adicionarEspacoAntesEDepois = (texto) => {
    // Primeiro, armazene as quebras de linha em um array para preservá-las
    const quebrasDeLinha = [];
    texto = texto.replace(/\n/g, (match, offset) => {
      const id = quebrasDeLinha.length;
      quebrasDeLinha.push(offset);
      return `\n${id}`;
    });

    texto = texto.replace(
      /([A-Za-z0-9])\s*([,;.])\s*(?=[A-Za-z0-9]|$)/g,
      '$1 $2 '
    );
  
    quebrasDeLinha.forEach(id => {
      texto = texto.replace(`\n${id}`, '\n');
    });
  
    return texto;
  };
  
  const handleRunClick = () => {
    if(!activeTab.content){
      setIsPopupOpen(true);
      return;
    }
    setIsLoading(true);
    setErrors([]);
    fetch('http://localhost:5000/enviar_conteudo', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: activeTab.content
    })
      .then(res => res.json())
      .then(data => {
        setTable(data.tabela);
        setSintatico(data.sintatico);
        
        if (data.sintatico && Array.isArray(data.sintatico) && data.sintatico.length > 0) {
          const formattedErrors = data.sintatico.map(error => ({
            line: error[0],        
            column: 0,             
            message: error[1]     
          }));
          setErrors(formattedErrors);
        } else {
          setErrors([]);
        }
        
        setPanelVisible(true);
        setIsLoading(false);
      })
      .catch(err => {
        console.error('Erro ao executar o código:', err);
        setIsLoading(false);
      });
  };

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
  }, [activeTab]);

  return (
    <div className="app-container">
      <input
        type="file"
        accept=".txt"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <MenuBar
        menus={menus}
        onToggle={handleMenuToggle}
        showDeclVars={showDeclVars}
        setShowDeclVars={setShowDeclVars}
        onAction={handleMenuAction}
      />
      <Tabs
        tabs={tabs}
        activeTabId={activeTabId}
        onSelect={setActiveTabId}
        onClose={removeTab}
      />
      <main className="content">
        {activeTab && activeTab.type === 'editor' && (
          <div style={{ position: 'relative', height: '100%' }}>
            <Editor
              value={activeTab.content}
              onChange={text => updateTabContent(activeTabId, text)}
              errors={errors}
            />
            <button className="run-button" onClick={handleRunClick}>▶</button>
          </div>
        )}
        {activeTab && activeTab.type === 'table' && (
          <Table type={activeTab.title} tableData={table} />
        )}
        {activeTab && activeTab.type === 'CsvTable' && (
          <CsvTable type={activeTab.title} tabela={csvText} />
        )}
      </main>
      {isLoading ? (
        <div>Carregando ...</div>
      ) : (
        panelVisible && (
          <Panel height={panelHeight} onStartResize={startResize} table={table} sintatico={sintatico} />
        )
      )}
      <button
        className="toggle-panel-btn"
        onClick={() => setPanelVisible(v => !v)}
      >
        {panelVisible ? 'Ocultar Painel' : 'Mostrar Painel'}
      </button>
      <Popup isOpen={isPopupOpen} onClose={() => setIsPopupOpen(false)}>
        <p>Antes de executar o compilador escreva um programa em linguagem LALG.</p>
      </Popup>
    </div>
  );
}
