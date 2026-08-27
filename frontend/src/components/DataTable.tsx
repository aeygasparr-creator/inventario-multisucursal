import type { ReactNode } from "react";

export interface Column<T> {
  header: string;
  accessor: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: (row: T) => string;
  emptyMessage?: string;
}

export default function DataTable<T>({ columns, data, keyField, emptyMessage }: DataTableProps<T>) {
  if (data.length === 0) {
    return <p className="empty-state">{emptyMessage || "No hay datos todavía."}</p>;
  }
  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.header}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={keyField(row)}>
              {columns.map((col) => (
                <td key={col.header}>{col.accessor(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
