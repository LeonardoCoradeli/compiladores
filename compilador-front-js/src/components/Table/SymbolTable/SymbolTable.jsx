import React from 'react';
import '../Table/Table.css';

export default function SymbolTable({ symbolData }) {
  return (
    <div className="symbol-table-container">
      {Object.entries(symbolData).map(([scope, symbols]) => (
        <div key={scope} className="scope-section">
          <h3>Escopo: {scope}</h3>
          <table>
            <thead>
              <tr>
                <th>Categoria</th>
                <th>Lexema</th>
                <th>Linha</th>
                <th>Tipo</th>
                <th>Endereço</th>
                <th>Utilizada</th>
              </tr>
            </thead>
            <tbody>
              {symbols.map((symbol, index) => (
                <tr key={index}>
                  <td>{symbol.Categoria}</td>
                  <td>{symbol.Lexema}</td>
                  <td>{symbol.Linha === null ? '-' : symbol.Linha}</td>
                  <td>{symbol.Tipo}</td>
                  <td>{symbol.Endereco || '-'}</td>
                  <td>{symbol.Utilizada ? 'Sim' : 'Não'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}