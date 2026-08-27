import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Link } from "react-router-dom";
import api from "../api/client";
import StatCard from "../components/StatCard";
import { useAuth } from "../auth/AuthContext";
import type {
  AlertaStock,
  OrdenCompra,
  Producto,
  Sucursal,
  Venta,
  VentasPorPeriodo,
} from "../types";

function formatearFecha(fecha: Date) {
  return fecha.toLocaleDateString("es-PE", { weekday: "long", day: "numeric", month: "long" });
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [sucursales, setSucursales] = useState<Sucursal[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [alertas, setAlertas] = useState<AlertaStock[]>([]);
  const [ventasHoy, setVentasHoy] = useState<Venta[]>([]);
  const [ordenesPendientes, setOrdenesPendientes] = useState<OrdenCompra[]>([]);
  const [tendencia, setTendencia] = useState<{ periodo: string; monto_total: number }[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function cargar() {
      const hoy = new Date();
      const hace7Dias = new Date();
      hace7Dias.setDate(hoy.getDate() - 6);
      const fechaInicio = hace7Dias.toISOString().slice(0, 10);
      const fechaHoy = hoy.toISOString().slice(0, 10);

      const [sucRes, prodRes, alertRes, ventasRes, ordenesRes, periodoRes] = await Promise.all([
        api.get<Sucursal[]>("/sucursales/"),
        api.get<Producto[]>("/productos/"),
        api.get<AlertaStock[]>("/reportes/alertas-stock"),
        api.get<Venta[]>("/ventas/"),
        api.get<OrdenCompra[]>("/ordenes-compra/"),
        api.get<VentasPorPeriodo[]>("/reportes/ventas-por-periodo", {
          params: { fecha_inicio: fechaInicio },
        }),
      ]);

      setSucursales(sucRes.data);
      setProductos(prodRes.data);
      setAlertas(alertRes.data);
      setVentasHoy(ventasRes.data.filter((v) => v.fecha.slice(0, 10) === fechaHoy));
      setOrdenesPendientes(ordenesRes.data.filter((o) => o.estado === "pendiente"));
      setTendencia(
        periodoRes.data.map((row) => ({
          periodo: new Date(row.periodo).toLocaleDateString("es-PE", {
            day: "numeric",
            month: "short",
          }),
          monto_total: Number(row.monto_total),
        })),
      );
      setCargando(false);
    }
    cargar();
  }, []);

  if (cargando) return <p className="loading">Cargando panel...</p>;

  const montoVentasHoy = ventasHoy.reduce((acc, v) => acc + Number(v.total), 0);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">🎛️ Panel central</h1>
          <p className="page-subtitle">
            Bienvenido, {user?.rol} · {formatearFecha(new Date())}
          </p>
        </div>
        <div className="page-actions">
          <Link className="btn btn-ghost" to="/inventario">
            ⇄ Transferir stock
          </Link>
          <Link className="btn btn-primary" to="/ventas">
            + Nueva venta
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard label="Sucursales activas" value={sucursales.length} />
        <StatCard label="Productos" value={productos.length} />
        <StatCard label="Ventas de hoy" value={`S/ ${montoVentasHoy.toFixed(2)}`} accent="gold" />
        <StatCard
          label="Órdenes pendientes"
          value={ordenesPendientes.length}
          accent={ordenesPendientes.length > 0 ? "red" : "gold"}
        />
        <StatCard
          label="Alertas de stock"
          value={alertas.length}
          accent={alertas.length > 0 ? "red" : "gold"}
        />
      </div>

      <div className="card">
        <h2>Tendencia de ventas (últimos 7 días)</h2>
        {tendencia.length === 0 ? (
          <p className="empty-state">Todavía no hay ventas suficientes para mostrar una tendencia.</p>
        ) : (
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <LineChart data={tendencia}>
                <XAxis dataKey="periodo" stroke="#b8a888" fontSize={12} />
                <YAxis stroke="#b8a888" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "#171010",
                    border: "1px solid rgba(212, 175, 55, 0.35)",
                    color: "#f2e9d8",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="monto_total"
                  stroke="#d4af37"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {alertas.length > 0 && (
        <div className="card">
          <h2>Alertas de stock</h2>
          <ul className="alert-list">
            {alertas.map((a) => (
              <li key={a.inventario_id}>
                <strong>{a.producto_nombre}</strong> en {a.sucursal_nombre}: {a.stock_actual}{" "}
                unidades (mínimo {a.stock_minimo})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
