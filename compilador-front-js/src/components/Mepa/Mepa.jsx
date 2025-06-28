import React from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-github';
import '../Editor/Editor.css';
import useStore from '../../store/useStore';

export default function MepaEditor() {
  const { activeTabId, tabs, updateTabContent, handleInterpretMepa } = useStore();
  const activeTab = tabs.find(t => t.id === activeTabId);
  const value = activeTab?.content || '';

  const handleChange = (newValue) => {
    updateTabContent(activeTabId, newValue);
  };

  return (
    <div className="editor-container">
      <AceEditor
        mode="text"
        theme="github"
        value={value}
        onChange={handleChange}
        name="mepa-editor"
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