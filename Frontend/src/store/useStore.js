import { create } from 'zustand';

let nextTabId = 1;

const useStore = create((set, get) => ({
  // Menus state
  menus: { Arquivos: false, Tabelas: false, Símbolos: false },
  setMenus: (menus) => set({ menus }),
  
  // Handler para toggle de menu
  toggleMenu: (menu) => set(state => {
    const newMenus = { ...state.menus, [menu]: !state.menus[menu] };
    // Reset showDeclVars quando o menu Tabelas é fechado
    if (menu === 'Tabelas' && state.menus[menu]) {
      return { menus: newMenus, showDeclVars: false };
    }
    return { menus: newMenus };
  }),

  // Editor and tabs state
  tabs: [{ id: nextTabId++, title: 'Editor 1', type: 'editor', content: '', language: 'lalg' }],
  activeTabId: 1,
  setTabs: (tabs) => set({ tabs }),
  setActiveTabId: (activeTabId) => set({ activeTabId }),
  addTab: ({ title, type, content = '', language = 'lalg', tableData = null }) => {
    const id = nextTabId++;
    set((state) => ({
      tabs: [...state.tabs, { id, title, type, content, language, tableData }],
      activeTabId: id
    }));
  },
  removeTab: (id) => {
    const state = get();
    if (state.tabs.length <= 1) return;
    
    const newTabs = state.tabs.filter(t => t.id !== id);
    set({
      tabs: newTabs,
      activeTabId: state.activeTabId === id ? newTabs[0].id : state.activeTabId
    });
  },
  updateTabContent: (id, content) => 
    set((state) => ({
      tabs: state.tabs.map(t => t.id === id ? { ...t, content } : t)
    })),

  // Panel state
  setPanelVisible: (visible) => set({ panelVisible: visible }),


  handleRunClick: async () => {
    state.setPanelVisible(true);
  },
  
  // Analysis state
  table: null,
  setTable: (table) => set({ table }),
  sintatico: null,
  setSintatico: (sintatico) => set({ sintatico }),
  csvText: '',
  setCsvText: (csvText) => set({ csvText }),
  tabelaSimbolos: null,
  setTabelaSimbolos: (tabelaSimbolos) => set({ tabelaSimbolos }),
  mepaCode: null,
  setMepaCode: (mepaCode) => set({ mepaCode }),
  
  // UI state
  isLoading: false,
  setIsLoading: (isLoading) => set({ isLoading }),
  errors: [],
  setErrors: (errors) => set({ errors }),
  warnings: [],
  setWarnings: (warnings) => set({warnings}),
  isPopupOpen: false,
  setIsPopupOpen: (isPopupOpen) => set({ isPopupOpen }),
  showDeclVars: false,
  setShowDeclVars: (showDeclVars) => set({ showDeclVars }),
  
  // Resize state (modificado)
  resizing: false,
  setResizing: (resizing) => set({ resizing }), // Adicionado

  // Utility functions
  clearAnalysisState: () => set({
    errors: [],
    table: null,
    sintatico: null,
    semantico: null,
    tabelaSimbolos: null,
    mepaCode: null,
    panelVisible: false
  }),

  handleMenuAction: async (action, fileInputRef) => {
    const {
        tabs, activeTabId, updateTabContent, clearAnalysisState, addTab, table, setIsPopupOpen, setIsLoading, setTabelaSimbolos, setPanelVisible, setErrors, setMepaCode, setTable, setSintatico, setSemantico, tabelaSimbolos
    } = get();
    const activeTab = tabs.find(t => t.id === activeTabId);
    switch (action) {
        case 'Salvar arquivo': {
        if (!activeTab || activeTab.type !== 'editor') return;
        const blob = new Blob([activeTab.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${activeTab.title}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        break;
        }
        case 'Carregar arquivo':
        if (fileInputRef && fileInputRef.current) fileInputRef.current.click();
        break;
        case 'Novo Arquivo': {
        const replace = window.confirm(
            'Substituir o conteúdo da aba atual?\nClique em Cancelar para criar nova aba em branco.'
        );
        if (replace && activeTab.type === 'editor') {
            updateTabContent(activeTabId, '');
            clearAnalysisState();
        } else {
            addTab({ title: `Editor ${tabs.length + 1}`, type: 'editor' });
            clearAnalysisState();
        }
        break;
        }
        case 'Lexico':
        case 'Léxicos': {
          const activeTab = tabs.find(t => t.id === activeTabId);
          if (!activeTab || !activeTab.content) {
            setIsPopupOpen(true);
            return;
          }
          
          if (table) {
            addTab({ title: 'Tabela Léxicos', type: 'table' });
          } else {
            // Executa a análise e depois abre a tabela
            get().handleRunClick()
              .then(() => {
                // Após execução, verifica se temos tabela
                if (get().table) {
                  addTab({ title: 'Tabela Léxicos', type: 'table' });
                } else {
                  setIsPopupOpen(true);
                  setPopupMessage("Não foi possível gerar a tabela léxica");
                }
              })
              .catch(error => {
                console.error("Erro na execução:", error);
                setIsPopupOpen(true);
                setPopupMessage("Erro ao tentar analisar o código");
              });
          }
          break;
        }
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
    },

    interpretationResult: null,
    setInterpretationResult: (result) => set({ interpretationResult: result }),

    // Função para interpretar o código MEPA
    handleInterpreterMepa: async () => {
      const state = get();
      const mepaCode = state.mepaCode;
      
      if (!mepaCode || mepaCode.length === 0) {
        state.setIsPopupOpen(true);
        return;
      }
      
      state.setIsLoading(true);
      
      try {
        const res = await fetch('http://localhost:5000/interpretar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mepa_code: mepaCode })
        });
        
        if (!res.ok) {
          throw new Error(`Erro na interpretação: ${res.status}`);
        }
        
        const data = await res.json();
        state.setInterpretationResult(data);
        
        // Adiciona uma aba para mostrar o resultado da interpretação
        state.addTab({
          title: `Resultado Interpretação`,
          type: 'interpretationResult',
          content: data,
          language: 'json'
        });
        
      } catch (err) {
        console.error('Erro ao interpretar código MEPA:', err);
        state.setIsPopupOpen(true);
      } finally {
        state.setIsLoading(false);
      }
    },

    handleFileChange: (e) => {
    const { tabs, activeTabId, updateTabContent, clearAnalysisState, addTab } = get();
    const activeTab = tabs.find(t => t.id === activeTabId);
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
        clearAnalysisState();
        } else {
        addTab({ title: file.name.replace(/\\.txt$/, ''), type: 'editor', content: text });
        clearAnalysisState();
        }
        e.target.value = null;
    };
    reader.readAsText(file);
    },

    handleRunClick: async () => {
      const state = get();
      const activeTab = state.tabs.find(t => t.id === state.activeTabId);
      
      if (!activeTab || !activeTab.content) {
        state.setIsPopupOpen(true);
        return Promise.reject("Nenhum conteúdo para executar");
      }
      
      state.setIsLoading(true);
      state.setErrors([]);
      
      try {
        const res = await fetch('http://localhost:5000/enviar_conteudo', {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: activeTab.content
        });
        
        const data = await res.json();
        
        state.setTable(data.tabela_lexica);
        state.setTabelaSimbolos(data.tabela_simbolos);
        state.setMepaCode(data.mepa_code);

        // Processar diferentes tipos de erros
        const allErrors = [];
        const warnings = [];

        // Erros léxicos
        if (data.erros?.lexico) {
          allErrors.push(...data.erros.sintaxe.map(error => ({
            line: error.linha,
            column: 0,
            message: error.mensagem,
            errorType: 'syntactic'
          })));
        }
        
        // Erros sintáticos
        if (data.erros?.sintaxe) {
          allErrors.push(...data.erros.sintaxe.map(error => ({
            line: error.linha,
            column: 0,
            message: error.mensagem,
            errorType: 'syntactic'
          })));
        }
        
        // Erros semânticos
        if (data.erros?.semantica_erros) {
          allErrors.push(...data.erros.semantica_erros.map(error => ({
            line: error.Linha,
            column: 0,
            message: error.Mensagem,
            errorType: 'semantic'
          })));
        }
        
        // Avisos semânticos
        if (data.erros?.semantica_avisos) {
          warnings.push(...data.erros.semantica_avisos.map(error => ({
            line: error.Linha,
            column: 0,
            message: error.Mensagem,
            errorType: 'semantic-warning'
          })));
        }

        state.setErrors(allErrors);
        state.setWarnings(warnings);
        state.setPanelVisible(true); 
        state.setIsLoading(false);

        // Se não houver erros, adicionar aba com código MEPA
        if (allErrors.length === 0) {
          state.addTab({
            title: `Código MEPA - ${activeTab.title}`,
            type: 'mepa',
            content: formatarCodigoMepa(data.mepa_code),
            language: 'mepa',
            sourceEditorId: activeTab.id
          });
        }
        
        return data;
      } catch (err) {
        console.error('Erro ao executar o código:', err);
        state.setIsLoading(false);
        throw err;
      }
    },

    // Função utilitária para formatação
    adicionarEspacoAntesEDepois: (texto) => {
      // Implementação da função
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
    },

    // Novo efeito para buscar CSV quando a aba muda
    fetchCsvForActiveTab: async () => {
      const state = get();
      const activeTab = state.tabs.find(t => t.id === state.activeTabId);
      
      if (activeTab && activeTab.type === 'CsvTable') {
        state.setIsLoading(true);
        try {
          const res = await fetch(`http://localhost:5000/tabela/${activeTab.title}`);
          if (!res.ok) throw new Error(`Status ${res.status}`);
          
          const data = await res.json();
          state.setCsvText(data.tabela);
        } catch (err) {
          console.error('Erro ao buscar CSV:', err);
          state.setCsvText('');
        } finally {
          state.setIsLoading(false);
        }
      }
    }
}));

export default useStore;

function formatarCodigoMepa(codigoMepa) {
  // Função interna para formatar um comando individual
  const formatarComando = (comando) => {
    if (!Array.isArray(comando)) return "";
    
    // Converte todos os elementos para string
    const elementos = comando.map(elemento => 
      typeof elemento === 'string' ? elemento : String(elemento)
    );
    
    // O mnemônico sempre na coluna 0
    let linhaFormatada = elementos[0];
    
    // Adiciona operandos a partir da coluna 10
    if (elementos.length > 1) {
      linhaFormatada = linhaFormatada.padEnd(10);
      linhaFormatada += elementos.slice(1).join(", ");
    }
    
    return linhaFormatada;
  };

  // Verifica o tipo de entrada
  if (Array.isArray(codigoMepa)) {
    return codigoMepa.map(formatarComando).join('\n');
  } else if (typeof codigoMepa === 'string') {
    try {
      const parsed = JSON.parse(codigoMepa);
      return parsed.map(formatarComando).join('\n');
    } catch (e) {
      return codigoMepa; // Fallback: retorna o original se não for JSON válido
    }
  }
  return formatarComando(codigoMepa);
}