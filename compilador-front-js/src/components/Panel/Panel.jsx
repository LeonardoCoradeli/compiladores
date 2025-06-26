import React from 'react';
import './Panel.css';

export default function Panel({ height, onStartResize, table, sintatico, semantico }) {
  const hasLexicalErrors = table?.erro?.linha && table.erro.linha.length > 0;
  const hasSyntacticError = sintatico && sintatico.length > 0;
  
  // Separar erros e avisos semânticos
  const semanticErrors = semantico?.filter(e => !e.mensagem.startsWith('Aviso:')) || [];
  const semanticWarnings = semantico?.filter(e => e.mensagem.startsWith('Aviso:')) || [];
  
  const hasSemanticErrors = semanticErrors.length > 0;
  const hasSemanticWarnings = semanticWarnings.length > 0;
  
  // Condição para mostrar sucesso (considerando apenas erros, não avisos)
  const showSuccess = !hasLexicalErrors && !hasSyntacticError && !hasSemanticErrors;

  return (
    <div className="resizable-panel" style={{ height }}>
      <div className="resize-handle" onMouseDown={onStartResize} />
      <div className="panel-content">
        {/* Erros Léxicos */}
        {hasLexicalErrors && (
          <div className="error-section">
            <h3>Erros Léxicos Encontrados:</h3>
            <ul>
              {table.erro.linha.map((linha, i) => (
                <li key={`lex-${i}`} className="error-item lexical-error">
                  <strong>Linha {linha}:</strong> Coluna {table.erro.col_ini[i]} a {table.erro.col_fin[i]}
                  <br />
                  {table.erro.erro[i]}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Erros Sintáticos */}
        {hasSyntacticError && (
          <div className="error-section">
            <h3>Erros Sintáticos Encontrados:</h3>
            <ul>
              {sintatico.map((error, i) => (
                <li className="error-item syntactic-error" key={`syn-${i}`}>
                  <strong>Linha {error[0]}:</strong> {error[1]}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Erros Semânticos */}
        {hasSemanticErrors && (
          <div className="error-section">
            <h3>Erros Semânticos Encontrados:</h3>
            <ul>
              {semanticErrors.map((error, i) => (
                <li className="error-item semantic-error" key={`sem-err-${i}`}>
                  <strong>Linha {error.linha}:</strong> {error.mensagem}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Avisos Semânticos */}
        {hasSemanticWarnings && (
          <div className="warning-section">
            <h3>Avisos Semânticos:</h3>
            <ul>
              {semanticWarnings.map((warning, i) => (
                <li className="warning-item" key={`sem-warn-${i}`}>
                  <strong>Linha {warning.linha}:</strong> {warning.mensagem}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Mensagem de sucesso */}
        {showSuccess && (
          <div className="success-section">
            <div className="success-icon">✓</div>
            <h3>Análise concluída com sucesso!</h3>
            <p>Nenhum erro léxico, sintático ou semântico foi encontrado.</p>
            <p>O código MEPA foi gerado e está disponível em uma nova aba.</p>
            
            {hasSemanticWarnings && (
              <div className="warning-note">
                <strong>Observação:</strong> Foram encontrados {semanticWarnings.length} aviso(s) semântico(s) que não impediram a compilação.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}