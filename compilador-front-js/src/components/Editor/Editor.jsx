import React, { useState } from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-github';
import './Editor.css';

export default function Editor({ value, onChange }) {
  const handleChange = (newValue) => {
    onChange(newValue);
  };

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
        setOptions={{
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true,
        }}
      />
    </div>
  );
}
