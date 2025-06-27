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

  // Função para limpar todos os estados de erro e análise
  const clearAnalysisState = () => {
    setErrors([]);
    setTable(null);
    setSintatico(null);
    setSemantico(null);
    setTabelaSimbolos(null);
    setMepaCode(null);
    setPanelVisible(false);
  };

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
          // Limpar erros quando criar novo arquivo
          clearAnalysisState();
        } else {
          addTab({ title: `Editor ${nextTabId}`, type: 'editor' });
          // Limpar erros quando criar nova aba
          clearAnalysisState();
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
        // Limpar erros quando carregar novo arquivo
        clearAnalysisState();
      } else {
        addTab({ title: file.name.replace(/\.txt$/, ''), type: 'editor', content: text });
        // Limpar erros quando carregar arquivo em nova aba
        clearAnalysisState();
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
        console.log('Resposta da API:', data); // Debug
        
        // Processar tabela léxica
        const lexicalTable = data.tabela_lexica || data.tabela;
        setTable(lexicalTable);
        
        // Verificar erros léxicos
        const hasLexicalErrors = lexicalTable?.erro?.linha?.length > 0;
        console.log('=== DEBUG ERROS LÉXICOS ===');
        console.log('lexicalTable:', lexicalTable);
        console.log('lexicalTable.erro:', lexicalTable?.erro);
        console.log('hasLexicalErrors:', hasLexicalErrors);
        console.log('Erros léxicos encontrados:', hasLexicalErrors, lexicalTable?.erro);
        
        // Processar erros sintáticos (nova estrutura da API)
        const sintaticoData = data.erros?.sintaxe || [];
        setSintatico(sintaticoData);
        console.log('Erros sintáticos encontrados:', sintaticoData.length, sintaticoData);
        
        // Verificar erros sintáticos
        const hasSyntacticErrors = sintaticoData?.length > 0;
        
        // Processar erros semânticos
        const semanticosErros = data.erros?.semantica_erros || [];
        const semanticosAvisos = data.erros?.semantica_avisos || [];
        const semanticoData = [...semanticosErros, ...semanticosAvisos];
        setSemantico(semanticoData);
        console.log('Erros semânticos encontrados:', semanticosErros.length, semanticosErros);
        console.log('Avisos semânticos encontrados:', semanticosAvisos.length, semanticosAvisos);
        
        // Verificar erros semânticos fatais (excluindo avisos)
        const hasSemanticErrors = semanticosErros.length > 0;
        
        // Configurar erros para o editor (léxicos, sintáticos e semânticos)
        let editorErrors = [];
        
        // Adicionar erros léxicos ao editor
        if (hasLexicalErrors && lexicalTable.erro?.linha) {
          console.log('=== PROCESSANDO ERROS LÉXICOS PARA EDITOR ===');
          console.log('lexicalTable.erro.linha:', lexicalTable.erro.linha);
          console.log('lexicalTable.erro.mensagem:', lexicalTable.erro.mensagem);
          
          const lexicalErrors = lexicalTable.erro.linha.map((linha, index) => ({
            line: linha,
            column: 0,
            message: `[ERRO LÉXICO] ${lexicalTable.erro.mensagem[index] || 'Erro léxico'}`,
            type: 'error',
            errorType: 'lexical' // Identificador para erros léxicos
          }));
          
          console.log('lexicalErrors criados:', lexicalErrors);
          editorErrors = [...editorErrors, ...lexicalErrors];
        }
        
        // Adicionar erros sintáticos ao editor
        if (hasSyntacticErrors) {
          const syntacticErrors = sintaticoData.map(error => ({
            line: error.linha,
            column: 0,
            message: `[ERRO SINTÁTICO] ${error.mensagem}`,
            type: 'error',
            errorType: 'syntactic' // Identificador para erros sintáticos
          }));
          editorErrors = [...editorErrors, ...syntacticErrors];
        }
        
        // Adicionar erros semânticos ao editor (destacar linha inteira)
        if (semanticosErros.length > 0) {
          const semanticErrors = semanticosErros.map(error => {
            const linha = parseInt(error.linha || error.Linha || 1);
            const mensagem = error.mensagem || error.Mensagem || '';
            
            return {
              line: Math.max(1, linha), // Garantir que linha seja pelo menos 1
              column: 0, // Começar do início da linha
              message: `[ERRO SEMÂNTICO] ${mensagem}`,
              type: 'error',
              errorType: 'semantic' // Usar errorType como os outros tipos de erro
            };
          });
          console.log('Semantic errors for editor:', semanticErrors); // Debug
          editorErrors = [...editorErrors, ...semanticErrors];
        }
        
        // Adicionar avisos semânticos ao editor (destacar linha inteira)
        if (semanticosAvisos.length > 0) {
          const semanticWarnings = semanticosAvisos.map(warning => {
            const linha = parseInt(warning.linha || warning.Linha || 1);
            const mensagem = warning.mensagem || warning.Mensagem || '';
            
            return {
              line: Math.max(1, linha), // Garantir que linha seja pelo menos 1
              column: 0, // Começar do início da linha
              message: `[AVISO SEMÂNTICO] ${mensagem}`,
              type: 'warning',
              errorType: 'semantic-warning' // Usar errorType consistente
            };
          });
          console.log('Semantic warnings for editor:', semanticWarnings); // Debug
          editorErrors = [...editorErrors, ...semanticWarnings];
        }
        
        setErrors(editorErrors);
        console.log('Total de erros enviados para o editor:', editorErrors.length, editorErrors);
        
        // Armazenar código MEPA e tabela de símbolos
        setMepaCode(data.mepa_code);
        setTabelaSimbolos(data.tabela_simbolos);
        
        // Verificar se podemos gerar código MEPA (apenas se não houver NENHUM erro, mas avisos são permitidos)
        const canGenerateMepa = !hasLexicalErrors && !hasSyntacticErrors && !hasSemanticErrors && data.mepa_code && data.mepa_code.length > 0;
        
        // Se não houver erros fatais, criar aba com código MEPA
        if (canGenerateMepa) {
          // Converter array de arrays em string
          const mepaText = data.mepa_code.map(line => 
            Array.isArray(line) ? line.join(' ') : line.toString()
          ).join('\n');
          
          addTab({
            title: 'Código MEPA',
            type: 'editor',
            content: mepaText,
            language: 'text'
          });
          
          // Limpar erros ao abrir tela do MEPA para manter interface limpa
          clearAnalysisState();
        }

        // Exibir painel se houver qualquer tipo de erro ou aviso
        const hasSemanticWarnings = semanticosAvisos.length > 0;
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