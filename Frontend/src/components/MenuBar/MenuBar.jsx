import React, { useRef } from 'react';
import './MenuBar.css';
import useStore from '../../store/useStore';

export default function MenuBar() {
  // Cria uma referência para o input de arquivo
  const fileInputRef = useRef(null);
  
  const { 
    menus, 
    setMenus, 
    showDeclVars, 
    setShowDeclVars,
    handleMenuAction,
    handleRunClick,
    handleFileChange
  } = useStore();

  return (
    <header className="header">
      {/* Input de arquivo oculto */}
      <input 
        type="file" 
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".txt"
        onChange={handleFileChange}  // Conecta ao handler do store
      />
      
      {['Arquivos', 'Tabelas', 'Símbolos'].map(menu => (
        <div
          key={menu}
          className="menu-item"
          onMouseEnter={() => setMenus({ ...menus, [menu]: true })}
          onMouseLeave={() => setMenus({ ...menus, [menu]: false })}
        >
          {menu}
          {menus[menu] && (
            <div className="submenu">
              {menu === 'Arquivos' && ['Salvar arquivo', 'Carregar arquivo', 'Novo Arquivo'].map(item => (
                <div 
                  key={item} 
                  className="submenu-item" 
                  onClick={() => handleMenuAction(item, fileInputRef)}  // Passa a referência
                >
                  {item}
                </div>
              ))}
              
              {menu === 'Tabelas' && (
                <>
                  <div className="submenu-item" onClick={() => handleMenuAction('Lexico')}>Lexico</div>
                  <div className="submenu-item nested">
                    <span onClick={() => setShowDeclVars(v => !v)} className="submenu-label">Sintático</span>
                    {showDeclVars && (
                      <div className="subnested">
                        <div className="submenu-item" onClick={() => handleMenuAction('Programa')}>Programa e Declarações</div>
                        <div className="submenu-item" onClick={() => handleMenuAction('Comandos')}>Comandos</div>
                        <div className="submenu-item" onClick={() => handleMenuAction('Expressoes')}>Expressões</div>
                        <div className="submenu-item" onClick={() => handleMenuAction('Completo')}>Tabela Completa</div>
                      </div>
                    )}
                  </div>
                </>
              )}
              
              {menu === 'Símbolos' && (
                <div className="submenu-item" onClick={() => handleMenuAction('TabelaSimbolos')}>
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