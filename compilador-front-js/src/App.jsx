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
  const [menus, setMenus] = useState({ Arquivos: false, Tabelas: false, Símbolos: false });
  const [showDeclVars, setShowDeclVars] = useState(false);
  const [panelVisible, setPanelVisible] = useState(false);
  const [panelHeight, setPanelHeight] = useState(200);
  const [tabs, setTabs] = useState([
    { id: nextTabId++, title: 'Editor 1', type: 'editor', content: '', language: 'lalg' }
  ]);
  const [activeTabId, setActiveTabId] = useState(tabs[0].id);
  const [table, setTable] = useState(null);
  const [sintatico, setSintatico] = useState(null);
  const [semantico, setSemantico] = useState(null);
  const [csvText, setCsvText] = useState('');
  const [tabelaSimbolos, setTabelaSimbolos] = useState(null);
  const [mepaCode, setMepaCode] = useState(null);
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

  const addTab = ({ title, type, content = '', language = 'lalg', tableData = null }) => {
    const id = nextTabId++;
    setTabs(ts => [...ts, { id, title, type, content, language, tableData }]);
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
      case 'Semantico':
      case 'Semântico':
        if (!activeTab || !activeTab.content) {
          setIsPopupOpen(true);
        } else {
          setIsLoading(true);
          fetch('http://localhost:5000/tabela_simbolos', {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain' },
            body: activeTab.content
          })
            .then(res => res.json())
            .then(data => {
              setTabelaSimbolos(data.tabela_simbolos);
              addTab({ 
                title: 'Tabela de Símbolos', 
                type: 'symbolTable',
                tableData: data.tabela_simbolos
              });
              setIsLoading(false);
            })
            .catch(() => {
              setIsPopupOpen(true);
              setIsLoading(false);
            });
        }
        break;
      case 'TabelaSimbolos':
        if (tabelaSimbolos) {
          addTab({
            title: 'Tabela de Símbolos',
            type: 'symbolTable',
            tableData: tabelaSimbolos
          });
        } else {
          setIsPopupOpen(true);
        }
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
  };

  const startResize = () => {
    resizing.current = true;
    if (!panelVisible) setPanelVisible(true);
  };

  const handleRunClick = () => {
    if(!activeTab.content){
      setIsPopupOpen(true);
      return;
    }
    setIsLoading(true);
    setErrors([]);
    setMepaCode(null);
    setTable(null);
    setSintatico(null);
    setSemantico(null);
    
    fetch('http://localhost:5000/enviar_conteudo', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: activeTab.content
    })
      .then(res => res.json())
      .then(data => {
        // Processar tabela léxica e erros
        const lexicalTable = data.tabela_lexica || data.tabela;
        setTable(lexicalTable);
        
        // Verificar erros léxicos
        const hasLexicalErrors = lexicalTable?.erro?.linha?.length > 0;
        
        // Processar erros sintáticos
        let sintaticoRaw = (data.resultado_analise && data.resultado_analise.sintaxe) || data.sintatico;
        let sintaticoArr = sintaticoRaw;
        if (Array.isArray(sintaticoRaw) && sintaticoRaw.length > 0 && sintaticoRaw[0] && 
            typeof sintaticoRaw[0] === 'object' && sintaticoRaw[0].linha !== undefined && 
            sintaticoRaw[0].mensagem !== undefined) {
          sintaticoArr = sintaticoRaw.map(e => [e.linha, e.mensagem]);
        }
        setSintatico(sintaticoArr);
        
        // Verificar erros sintáticos
        const hasSyntacticErrors = sintaticoArr?.length > 0;
        
        // Processar erros semânticos
        const semanticoData = (data.resultado_analise && data.resultado_analise.semantica) || data.semantico;
        setSemantico(semanticoData);
        
        // Verificar erros semânticos (excluindo avisos)
        const semanticErrors = semanticoData?.filter(e => !e.mensagem.startsWith('Aviso:')) || [];
        const hasSemanticErrors = semanticErrors.length > 0;
        
        // Configurar erros para o editor
        if (hasSyntacticErrors) {
          const formattedErrors = sintaticoArr.map(error => ({
            line: error[0],
            column: 0,
            message: error[1]
          }));
          setErrors(formattedErrors);
        } else {
          setErrors([]);
        }
        
        // Armazenar código MEPA e tabela de símbolos
        setMepaCode(data.mepa_code);
        setTabelaSimbolos(data.tabela_simbolos);
        
        // Verificar se podemos gerar código MEPA
        const canGenerateMepa = !hasLexicalErrors && !hasSyntacticErrors && !hasSemanticErrors && data.mepa_code;
        
        // Se não houver erros, criar aba com código MEPA
        if (canGenerateMepa) {
          // Converter array de arrays em string
          const mepaText = data.mepa_code.map(line => line.join(' ')).join('\n');
          addTab({
            title: 'Código MEPA',
            type: 'editor',
            content: mepaText,
            language: 'text'
          });
        }

        // Exibir painel se houver qualquer tipo de erro ou aviso
        const hasSemanticWarnings = semanticoData?.filter(e => e.mensagem.startsWith('Aviso:'))?.length > 0;
        if (hasLexicalErrors || hasSyntacticErrors || hasSemanticErrors || hasSemanticWarnings) {
          setPanelVisible(true);
        }

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
              mode={activeTab.language}
            />
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
      </main>
      {isLoading ? (
        <div className="loading-indicator">Carregando...</div>
      ) : (
        panelVisible && (
          <Panel height={panelHeight} onStartResize={startResize} table={table} sintatico={sintatico} semantico={semantico} />
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