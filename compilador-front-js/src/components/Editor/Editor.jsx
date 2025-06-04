import React from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-github';
import './Editor.css';

export default function Editor({ value, onChange, errors = [] }) {
  const handleChange = (newValue) => {
    onChange(newValue);
  };

  console.log('Errors received in Editor:', errors);

  const annotations = errors.map((error, index) => {
    const annotation = {
      row: error.line - 1, // Ace Editor usa índice baseado em 0
      column: error.column || 0,
      text: error.message,
      type: 'error'
    };
    console.log(`Annotation ${index}:`, annotation);
    return annotation;
  });

  const markers = errors.map((error, index) => {
    const marker = {
      startRow: error.line - 1, // Ace Editor usa índice baseado em 0
      startCol: 0,
      endRow: error.line - 1,
      endCol: 1000, // Marca a linha inteira
      className: 'error-marker',
      type: 'fullLine',
      inFront: true // Garante que o marker apareça na frente
    };
    console.log(`Marker ${index}:`, marker);
    return marker;
  });

  return (
    <div className="editor-container">
      <AceEditor
        mode="text"
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