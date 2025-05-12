import React from 'react';
import './Panel.css';

export default function Panel({ height, onStartResize, table, sintatico }) {
  const hasLexicalErrors = table?.erro?.linha && table.erro.linha.length > 0;
  const hasSyntacticError = sintatico?.includes('Esperado');
  const hasSyntacticResult = sintatico && !hasSyntacticError;

  return (
    <div className="resizable-panel" style={{ height }}>
      <div className="resize-handle" onMouseDown={onStartResize} />
      <div className="panel-content">
        {hasLexicalErrors && (
          <div>
            <h3>Erros Léxicos Encontrados:</h3>
            <ul>
              {table.erro.linha.map((linha, i) => (
                <li key={i}>
                  Linha {linha}: Coluna {table.erro.col_ini[i]} a {table.erro.col_fin[i]}
                  <br />
                  {table.erro.erro[i]}
                </li>
              ))}
            </ul>
          </div>
        )}
        {hasSyntacticError && (
          <div>
            <h3>Erro Sintático Encontrado:</h3>
            <p>{sintatico}</p>
          </div>
        )}
        {hasSyntacticResult && (
          <p>{sintatico}</p>
        )}
      </div>
    </div>
  );
}