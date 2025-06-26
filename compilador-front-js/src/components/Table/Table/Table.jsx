import React from 'react';
import './Table.css';
import SymbolTable from '../SymbolTable/SymbolTable';

export default function Table({ type, tableData }) {
  if (type === 'TabelaSimbolos') {
    return <SymbolTable symbolData={tableData} />;
  }

  if (tableData.semantico) {
    const headers = ['Escopo', 'Linha', 'Mensagem'];
    const rows = tableData.semantico.map((item, idx) => [item.escopo, item.linha, item.mensagem]);
    return (
      <div className="table-container">
        <h3>{type}</h3>
        <table>
          <thead>
            <tr>{headers.map((header, i) => <th key={i}>{header}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                {r.map((c, j) => <td key={j}>{c}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Tabela léxica padrão
  const headers = ['Token', 'Lexema', 'Linha', 'Coluna Inicial', 'Coluna Final'];
  const rows = tableData.lexema.map((lexema, index) => [
    tableData.token[index],
    lexema,
    tableData.linha[index],
    tableData.col_ini[index],
    tableData.col_fin[index]
  ]);

  return (
    <div className="table-container">
      <h3>{type}</h3>
      <table>
        <thead>
          <tr>{headers.map((header, i) => <th key={i}>{header}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((c, j) => <td key={j}>{c}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
