import React from 'react';
import './Panel.css';
import useStore from '../../store/useStore';

export default function Panel() {
  const {
    panelHeight,
    errors,
    warnings
  } = useStore();
  
  // Cálculos baseados no array unificado de erros
  const lexicalErrors = errors.filter(e => e.errorType === 'lexical');
  const syntacticErrors = errors.filter(e => e.errorType === 'syntactic');
  const semanticErrors = errors.filter(e => e.errorType === 'semantic');
  const semanticWarnings = warnings
  
  const totalErrors = lexicalErrors.length + syntacticErrors.length + semanticErrors.length;
  const totalWarnings = semanticWarnings.length;
  
  const showSuccess = totalErrors === 0;

  return (
    <div 
      className="resizable-panel" 
      style={{ height: panelHeight }}
    >
      <div className="panel-content">
        <div className="compilation-status">
          <h3>Status da Compilação</h3>
          
          {showSuccess ? (
            <div className="success-section">
              <div className="success-icon">✓</div>
              <p className="success-message">Compilação concluída com sucesso!</p>
              <p>Todos os erros estão destacados no editor acima.</p>
              {totalWarnings > 0 && (
                <p className="warning-note">
                  {totalWarnings} aviso(s) encontrado(s) - veja os destaques amarelos no editor.
                </p>
              )}
            </div>
          ) : (
            <div className="error-summary">
              <div className="error-stats">
                {totalErrors > 0 && (
                  <div className="stat-item error-stat">
                    <span className="stat-number">{totalErrors}</span>
                    <span className="stat-label">Erro(s) encontrado(s)</span>
                  </div>
                )}
                {totalWarnings > 0 && (
                  <div className="stat-item warning-stat">
                    <span className="stat-number">{totalWarnings}</span>
                    <span className="stat-label">Aviso(s) encontrado(s)</span>
                  </div>
                )}
              </div>
              
              <div className="error-guide">
                <h4>Legenda de Cores no Editor:</h4>
                <ul>
                  <li><span className="color-indicator lexical-color"></span> Vermelho sólido: Erros Léxicos</li>
                  <li><span className="color-indicator syntactic-color"></span> Laranja sólido: Erros Sintáticos</li>
                  <li><span className="color-indicator semantic-error-color"></span> Laranja escuro: Erros Semânticos</li>
                  <li><span className="color-indicator semantic-warning-color"></span> Amarelo: Avisos Semânticos</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}