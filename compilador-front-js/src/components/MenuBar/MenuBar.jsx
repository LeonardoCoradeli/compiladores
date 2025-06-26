import React from 'react';
import './MenuBar.css';

export default function MenuBar({ menus, onToggle, showDeclVars, setShowDeclVars, onAction }) {
  return (
    <header className="header">
      {['Arquivos', 'Tabelas', 'Símbolos'].map(menu => (
        <div
          key={menu}
          className="menu-item"
          onMouseEnter={() => onToggle(menu)}
          onMouseLeave={() => onToggle(menu)}
        >
          {menu}
          {menus[menu] && (
            <div className="submenu">
              {menu === 'Arquivos' && ['Salvar arquivo', 'Carregar arquivo', 'Novo Arquivo'].map(item => (
                <div key={item} className="submenu-item" onClick={() => onAction(item)}>{item}</div>
              ))}
              
              {menu === 'Tabelas' && (
                <>
                  <div className="submenu-item" onClick={() => onAction('Lexico')}>Lexico</div>
                  <div className="submenu-item" onClick={() => onAction('Semantico')}>Semântico</div>
                  <div className="submenu-item nested">
                    <span onClick={() => setShowDeclVars(v => !v)} className="submenu-label">Sintático</span>
                    {showDeclVars && (
                      <div className="subnested">
                        <div className="submenu-item" onClick={() => onAction('Programa')}>Programa e Declarações</div>
                        <div className="submenu-item" onClick={() => onAction('Comandos')}>Comandos</div>
                        <div className="submenu-item" onClick={() => onAction('Expressoes')}>Expressões</div>
                        <div className="submenu-item" onClick={() => onAction('Completo')}>Tabela Completa</div>
                      </div>
                    )}
                  </div>
                </>
              )}
              
              {menu === 'Símbolos' && (
                <div className="submenu-item" onClick={() => onAction('TabelaSimbolos')}>
                  Exibir Tabela de Símbolos
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </header>
  );
}
