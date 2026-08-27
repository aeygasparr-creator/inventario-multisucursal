import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api/client";
import DataTable from "../components/DataTable";
import type {
  AlertaStock,
  ProductoMasVendido,
  RotacionStock,
  VentasPorPeriodo,
  VentasPorSucursal,
} from "../types";

interface PuntoGrafico {
  periodo: string;
  monto_total: number;
}

export default function ReportesPage() {
  const [productosTop, setProductosTop] = useState<ProductoMasVendido[]>([]);
  const [ventasSucursal, setVentasSucursal] = useState<VentasPorSucursal[]>([]);
  const [ventasPeriodo, setVentasPeriodo] = useState<PuntoGrafico[]>([]);
  const [alertas, setAlertas] = useState<AlertaStock[]>([]);
  const [rotacion, setRotacion] = useState<RotacionStock[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function cargar() {
      const [a, b, c, d, e] = await Promise.all([
        api.get<ProductoMasVendido[]>("/reportes/productos-mas-vendidos"),
        api.get<VentasPorSucursal[]>("/reportes/ventas-por-sucursal"),
        api.get<VentasPorPeriodo[]>("/reportes/ventas-por-periodo"),
        api.get<AlertaStock[]>("/reportes/alertas-stock"),
        api.get<RotacionStock[]>("/reportes/rotacion-stock"),
      ]);
      setProductosTop(a.data);
      setVentasSucursal(b.data);
      setVentasPeriodo(
        c.data.map((row) => ({
          periodo: new Date(row.periodo).toLocaleDateString("es-PE"),
          monto_total: Number(row.monto_total),
        })),
      );
      setAlertas(d.data);
      setRotacion(e.data);
      setCargando(false);
    }
    cargar();
  }, []);

  if (cargando) return <p className="loading">Cargando reportes...</p>;

  return (
    <div>
      <h1 className="page-title">📈 Reportes</h1>

      <div className="card">
        <h2>Ventas por periodo</h2>
        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={ventasPeriodo}>
              <CartesianGrid stroke="#241414" />
              <XAxis dataKey="periodo" stroke="#b8a888" fontSize={12} />
              <YAxis stroke="#b8a888" fontSize={12} />
              <Tooltip
                contentStyle={{ background: "#171010", border: "1px solid rgba(212, 175, 55, 0.35)", color: "#f2e9d8" }}
              />
              <Line type="monotone" dataKey="monto_total" stroke="#d4af37" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2>Productos más vendidos</h2>
        <DataTable
          columns={[
            { header: "Producto", accessor: (p: ProductoMasVendido) => p.nombre },
            { header: "SKU", accessor: (p: ProductoMasVendido) => p.sku },
            { header: "Unidades vendidas", accessor: (p: ProductoMasVendido) => p.cantidad_vendida },
            { header: "Monto", accessor: (p: ProductoMasVendido) => `S/ ${p.monto_vendido}` },
          ]}
          data={productosTop}
          keyField={(p) => p.producto_id}
          emptyMessage="Todavía no hay ventas registradas."
        />
      </div>

      <div className="card">
        <h2>Ventas por sucursal</h2>
        <DataTable
          columns={[
            { header: "Sucursal", accessor: (v: VentasPorSucursal) => v.nombre },
            { header: "Cantidad de ventas", accessor: (v: VentasPorSucursal) => v.cantidad_ventas },
            { header: "Monto total", accessor: (v: VentasPorSucursal) => `S/ ${v.monto_total}` },
          ]}
          data={ventasSucursal}
          keyField={(v) => v.sucursal_id}
          emptyMessage="Todavía no hay ventas registradas."
        />
      </div>

      <div className="card">
        <h2>Alertas de stock</h2>
        <DataTable
          columns={[
            { header: "Producto", accessor: (a: AlertaStock) => a.producto_nombre },
            { header: "Sucursal", accessor: (a: AlertaStock) => a.sucursal_nombre },
            { header: "Stock actual", accessor: (a: AlertaStock) => a.stock_actual },
            { header: "Stock mínimo", accessor: (a: AlertaStock) => a.stock_minimo },
          ]}
          data={alertas}
          keyField={(a) => a.inventario_id}
          emptyMessage="Sin alertas de stock por ahora."
        />
      </div>

      <div className="card">
        <h2>Rotación de stock (últimos 30 días)</h2>
        <DataTable
          columns={[
            { header: "Producto", accessor: (r: RotacionStock) => r.producto_nombre },
            { header: "Sucursal", accessor: (r: RotacionStock) => r.sucursal_nombre },
            { header: "Stock actual", accessor: (r: RotacionStock) => r.stock_actual },
            { header: "Vendido en periodo", accessor: (r: RotacionStock) => r.vendido_en_periodo },
            {
              header: "Índice de rotación",
              accessor: (r: RotacionStock) => (r.indice_rotacion === null ? "—" : r.indice_rotacion),
            },
          ]}
          data={rotacion}
          keyField={(r) => `${r.producto_id}-${r.sucursal_id}`}
          emptyMessage="Sin datos de rotación todavía."
        />
      </div>
    </div>
  );
}
