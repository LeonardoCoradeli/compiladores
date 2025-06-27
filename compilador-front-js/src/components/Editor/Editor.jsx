import React from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-github';
import './Editor.css';
import './Lalg.mode.register.jsx';

export default function Editor({ value, onChange, errors = [] }) {
  const handleChange = (newValue) => {
    onChange(newValue);
  };

  console.log('Errors received in Editor:', errors);

  // Debug específico para erros léxicos
  const lexicalErrors = errors.filter(error => error.errorType === 'lexical');
  console.log('Erros léxicos no Editor:', lexicalErrors);

  // Criar anotações para o gutter (margem lateral)
  const annotations = errors.map((error, index) => {
    // Mapear o tipo de erro para o tipo de annotation do Ace Editor
    let annotationType = 'error'; // padrão
    if (error.errorType === 'semantic-warning') {
      annotationType = 'warning';
    } else if (error.errorType === 'lexical') {
      annotationType = 'error';
    } else if (error.errorType === 'syntactic') {
      annotationType = 'error';
    } else if (error.errorType === 'semantic') {
      annotationType = 'error';
    }
    
    const annotation = {
      row: error.line - 1, // Ace Editor usa índice baseado em 0
      column: error.column || 0,
      text: error.message,
      type: annotationType
    };
    console.log(`Annotation ${index} (${error.errorType}):`, annotation);
    return annotation;
  });

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
        annotations={annotations}
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