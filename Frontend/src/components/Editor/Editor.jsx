import React from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-github';
import './Editor.css';
import './Lalg.mode.register.jsx';
import useStore from '../../store/useStore';

export default function Editor() {
  const { activeTabId, tabs, updateTabContent, errors, warnings } = useStore();
  const activeTab = tabs.find(t => t.id === activeTabId);
  const value = activeTab?.content || '';

  const handleChange = (newValue) => {
    updateTabContent(activeTabId, newValue);
  };

  console.log('Errors received in Editor:', errors);

  // Debug específico para erros léxicos
  const lexicalErrors = errors.filter(error => error.errorType === 'lexical');
  console.log('Erros léxicos no Editor:', lexicalErrors);

  // Criar anotações para o gutter (margem lateral)
  const errorAnnotations = errors.map(error => ({
    row: error.line - 1,       // Ace usa índice 0 para linhas
    column: error.column || 0,
    text: error.message,
    type: 'error'              // Defina o tipo como 'error' para todos eles
  }));

  // 2. Mapeie o array de AVISOS para o mesmo formato.
  const warningAnnotations = warnings.map(warning => ({
    row: warning.line - 1,
    column: warning.column || 0,
    text: warning.message,
    type: 'warning'            // Defina o tipo como 'warning' para todos eles
  }));

  // 3. Junte os dois arrays em um único array final de anotações.
  const allAnnotations = [...errorAnnotations, ...warningAnnotations];
  // Criar markers visuais para as linhas
  const markers = errors.map((error, index) => {
    const isLexicalError = error.errorType === 'lexical';
    const isSyntacticError = error.errorType === 'syntactic';
    const isSemanticError = error.errorType === 'semantic';
    const isSemanticWarning = error.errorType === 'semantic-warning';
    
    // Escolher estilo baseado no tipo de erro (todos destacam linha inteira):
    // - Erros léxicos: borda vermelha à esquerda (linha inteira)
    // - Erros sintáticos: borda laranja à esquerda (linha inteira)
    // - Erros semânticos: borda laranja escura à esquerda (linha inteira)
    // - Avisos semânticos: borda amarela à esquerda (linha inteira)
    let className = 'error-marker'; // Padrão para erros léxicos
    
    if (isLexicalError) {
      className = 'error-marker';
    } else if (isSyntacticError) {
      className = 'syntactic-error-marker';
    } else if (isSemanticError) {
      className = 'semantic-error-marker';
    } else if (isSemanticWarning) {
      className = 'semantic-warning-marker';
    }
    
    const marker = {
      startRow: error.line - 1,
      startCol: 0, // Sempre do início da linha
      endRow: error.line - 1,
      endCol: 1000, // Até o final da linha
      className: className,
      type: 'fullLine',
      inFront: true
    };
    console.log(`Marker ${index} (${error.errorType}) - Line ${error.line}:`, marker, 'className:', className);
    return marker;
  });

  return (
    <div className="editor-container">
      <AceEditor
        mode="lalg"
        theme="github"
        value={value}
        onChange={handleChange}
        name="editor"
        editorProps={{ $blockScrolling: true }}
        width="100%"
        height="100%"
        fontSize={14}
        showPrintMargin={false}
        showGutter={true}
        highlightActiveLine={true}
        annotations={allAnnotations}
        markers={markers}
        setOptions={{
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true,
        }}
      />
    </div>
  );
}