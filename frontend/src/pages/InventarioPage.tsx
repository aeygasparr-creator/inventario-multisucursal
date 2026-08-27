import { useEffect, useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { InventarioItem, Producto, Sucursal } from "../types";

export default function InventarioPage() {
  const [inventario, setInventario] = useState<InventarioItem[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [sucursales, setSucursales] = useState<Sucursal[]>([]);
  const [modalEntrada, setModalEntrada] = useState(false);
  const [modalTransferencia, setModalTransferencia] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const [productoId, setProductoId] = useState("");
  const [sucursalId, setSucursalId] = useState("");
  const [sucursalDestinoId, setSucursalDestinoId] = useState("");
  const [cantidad, setCantidad] = useState("");

  async function cargar() {
    const [invRes, prodRes, sucRes] = await Promise.all([
      api.get<InventarioItem[]>("/inventario/"),
      api.get<Producto[]>("/productos/"),
      api.get<Sucursal[]>("/sucursales/"),
    ]);
    setInventario(invRes.data);
    setProductos(prodRes.data);
    setSucursales(sucRes.data);
  }

  useEffect(() => {
    cargar();
  }, []);

  function nombreProducto(id: string) {
    return productos.find((p) => p.id === id)?.nombre || "—";
  }
  function nombreSucursal(id: string) {
    return sucursales.find((s) => s.id === id)?.nombre || "—";
  }

  function limpiarFormulario() {
    setProductoId("");
    setSucursalId("");
    setSucursalDestinoId("");
    setCantidad("");
  }

  function extraerError(err: unknown): string {
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      return String(err.response.data.detail);
    }
    return "Ocurrió un error inesperado";
  }

  async function registrarEntrada(e: FormEvent) {
    e.preventDefault();
    setMensaje(null);
    setEnviando(true);
    try {
      await api.post("/inventario/entradas", {
        producto_id: productoId,
        sucursal_id: sucursalId,
        cantidad: Number(cantidad),
        motivo: "Registrado desde el panel",
      });
      setModalEntrada(false);
      limpiarFormulario();
      cargar();
    } catch (err) {
      setMensaje(extraerError(err));
    } finally {
      setEnviando(false);
    }
  }

  async function registrarTransferencia(e: FormEvent) {
    e.preventDefault();
    setMensaje(null);
    setEnviando(true);
    try {
      await api.post("/inventario/transferencias", {
        producto_id: productoId,
        sucursal_origen_id: sucursalId,
        sucursal_destino_id: sucursalDestinoId,
        cantidad: Number(cantidad),
        motivo: "Transferencia registrada desde el panel",
      });
      setModalTransferencia(false);
      limpiarFormulario();
      cargar();
    } catch (err) {
      setMensaje(extraerError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🗃️ Inventario</h1>
        <div className="page-actions">
          <button
            className="btn btn-ghost"
            type="button"
            onClick={() => {
              setMensaje(null);
              setModalEntrada(true);
            }}
          >
            + Entrada de stock
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={() => {
              setMensaje(null);
              setModalTransferencia(true);
            }}
          >
            ⇄ Transferir stock
          </button>
        </div>
      </div>

      <DataTable
        columns={[
          { header: "Producto", accessor: (i: InventarioItem) => nombreProducto(i.producto_id) },
          { header: "Sucursal", accessor: (i: InventarioItem) => nombreSucursal(i.sucursal_id) },
          { header: "Stock actual", accessor: (i: InventarioItem) => i.stock_actual },
          { header: "Stock mínimo", accessor: (i: InventarioItem) => i.stock_minimo },
        ]}
        data={inventario}
        keyField={(i) => i.id}
        emptyMessage="Todavía no hay stock registrado."
      />

      {modalEntrada && (
        <Modal title="Registrar entrada de stock" onClose={() => setModalEntrada(false)}>
          <form onSubmit={registrarEntrada}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Producto</span>
              <select value={productoId} onChange={(e) => setProductoId(e.target.value)} required>
                <option value="">Selecciona un producto</option>
                {productos.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Sucursal</span>
              <select value={sucursalId} onChange={(e) => setSucursalId(e.target.value)} required>
                <option value="">Selecciona una sucursal</option>
                {sucursales.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Cantidad</span>
              <input
                type="number"
                min="1"
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                required
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={enviando}>
              {enviando ? "Registrando..." : "Registrar entrada"}
            </button>
          </form>
        </Modal>
      )}

      {modalTransferencia && (
        <Modal
          title="Transferir stock entre sucursales"
          onClose={() => setModalTransferencia(false)}
        >
          <form onSubmit={registrarTransferencia}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Producto</span>
              <select value={productoId} onChange={(e) => setProductoId(e.target.value)} required>
                <option value="">Selecciona un producto</option>
                {productos.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Sucursal origen</span>
              <select value={sucursalId} onChange={(e) => setSucursalId(e.target.value)} required>
                <option value="">Selecciona la sucursal de origen</option>
                {sucursales.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Sucursal destino</span>
              <select
                value={sucursalDestinoId}
                onChange={(e) => setSucursalDestinoId(e.target.value)}
                required
              >
                <option value="">Selecciona la sucursal de destino</option>
                {sucursales.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Cantidad</span>
              <input
                type="number"
                min="1"
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                required
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={enviando}>
              {enviando ? "Transfiriendo..." : "Transferir"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
