import React from 'react';
import './CsvTable.css';

export default function CsvTable({ type, tabela }) {
  const rows = tabela
    .trim()
    .split('\n')
    .map(line =>
      line.split(',').map(cell =>
        cell.replace(/\u00A0/g, '').trim()
      )
      
    );

  if (rows.length === 0) {
    return (
      <div className="table-container">
        <h3>{type}</h3>
        <p>Nenhum dado disponível.</p>
      </div>
    );
  }

  const headers = rows[0];
  const numHeaders = headers.length;
  const dataRows = rows.slice(1).map(row => {
    const diff = numHeaders - row.length;
    if (diff > 0) {
      return [...row, ...Array(diff).fill('')];
    } else if (diff < 0) {
      return row.slice(0, numHeaders);
    }
    return row;
  });

  return (
    <div className="table-container">
      <h3>{type}</h3>
      <table>
        <thead>
          <tr>
            {headers.map((header, i) => (
              <th key={i}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            <tr key={ri}>
              {row.map((cell, ci) => (
                <td key={ci}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}