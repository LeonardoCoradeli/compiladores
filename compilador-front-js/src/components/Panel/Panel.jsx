import React from 'react';
import './Panel.css';

export default function Panel({ height, onStartResize, table, sintatico, semantico }) {
  const hasLexicalErrors = table?.erro?.linha && table.erro.linha.length > 0;
  const hasSyntacticError = sintatico && sintatico.length > 0;
  const hasSemanticErrors = semantico && semantico.length > 0;

  const semanticErrors = semantico?.filter(e => !e.mensagem.startsWith('Aviso:')) || [];
  const semanticWarnings = semantico?.filter(e => e.mensagem.startsWith('Aviso:')) || [];

  return (
    <div className="resizable-panel" style={{ height }}>
      <div className="resize-handle" onMouseDown={onStartResize} />
      <div className="panel-content">
        {hasLexicalErrors && (
          <div>
            <h3>Erros Léxicos Encontrados:</h3>
            <ul>
              {table.erro.linha.map((linha, i) => (
                <li key={`lex-${i}`} style={{ color: '#E53E3E', marginBottom: '5px' }}>
                  <strong>Linha {linha}:</strong> Coluna {table.erro.col_ini[i]} a {table.erro.col_fin[i]}
                  <br />
                  {table.erro.erro[i]}
                </li>
              ))}
            </ul>
          </div>
        )}

        {hasSyntacticError && (
          <div>
            <h3>Erros Sintáticos Encontrados:</h3>
            <ul>
              {sintatico.map((error, i) => (
                <li style={{ padding: "1px", color: '#E53E3E' }} key={`syn-${i}`}>
                  <strong>Linha {error[0]}:</strong> {error[1]}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* <<< Bloco para exibir erros semânticos >>> */}
        {semanticErrors.length > 0 && (
          <div>
            <h3>Erros Semânticos Encontrados:</h3>
            <ul>
              {semanticErrors.map((error, i) => (
                <li style={{ padding: "1px", color: '#DD6B20' }} key={`sem-err-${i}`}>
                  <strong>Linha {error.linha}:</strong> {error.mensagem}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* <<< Bloco para exibir avisos semânticos (variáveis não usadas, etc.) >>> */}
        {semanticWarnings.length > 0 && (
          <div>
            <h3>Avisos Semânticos:</h3>
            <ul>
              {semanticWarnings.map((warning, i) => (
                <li style={{ padding: "1px", color: '#D69E2E' }} key={`sem-warn-${i}`}>
                  <strong>Linha {warning.linha}:</strong> {warning.mensagem}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* <<< Condição atualizada para mostrar a mensagem de sucesso >>> */}
        {!hasLexicalErrors && !hasSyntacticError && !hasSemanticErrors && (
          <div>
            <h3>Análise concluída com sucesso!</h3>
            <p>Nenhum erro léxico, sintático ou semântico foi encontrado.</p>
          </div>
        )}
      </div>
    </div>
  );
}
