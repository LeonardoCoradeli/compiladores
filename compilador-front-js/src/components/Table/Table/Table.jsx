import React from 'react';
import './Table.css';

export default function Table({ type, tableData }) {
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
