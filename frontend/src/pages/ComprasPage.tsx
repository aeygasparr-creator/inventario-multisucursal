import { useEffect, useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { OrdenCompra, Producto, Proveedor, Sucursal } from "../types";

interface ItemForm {
  producto_id: string;
  cantidad: string;
  precio_unitario: string;
}

const ITEM_VACIO: ItemForm = { producto_id: "", cantidad: "", precio_unitario: "" };

const EMOJI_ESTADO: Record<string, string> = {
  pendiente: "⏳",
  recibida: "✅",
  cancelada: "✕",
};

export default function ComprasPage() {
  const [ordenes, setOrdenes] = useState<OrdenCompra[]>([]);
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [sucursales, setSucursales] = useState<Sucursal[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [proveedorId, setProveedorId] = useState("");
  const [sucursalId, setSucursalId] = useState("");
  const [items, setItems] = useState<ItemForm[]>([{ ...ITEM_VACIO }]);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  async function cargar() {
    const [ordRes, provRes, sucRes, prodRes] = await Promise.all([
      api.get<OrdenCompra[]>("/ordenes-compra/"),
      api.get<Proveedor[]>("/proveedores/"),
      api.get<Sucursal[]>("/sucursales/"),
      api.get<Producto[]>("/productos/"),
    ]);
    setOrdenes(ordRes.data);
    setProveedores(provRes.data);
    setSucursales(sucRes.data);
    setProductos(prodRes.data);
  }

  useEffect(() => {
    cargar();
  }, []);

  function nombreProveedor(id: string) {
    return proveedores.find((p) => p.id === id)?.razon_social || "—";
  }
  function nombreSucursal(id: string) {
    return sucursales.find((s) => s.id === id)?.nombre || "—";
  }

  function actualizarItem(index: number, campo: keyof ItemForm, valor: string) {
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, [campo]: valor } : it)));
  }

  function agregarItem() {
    setItems((prev) => [...prev, { ...ITEM_VACIO }]);
  }

  function quitarItem(index: number) {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  function extraerError(err: unknown, fallback: string): string {
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      return String(err.response.data.detail);
    }
    return fallback;
  }

  async function crearOrden(e: FormEvent) {
    e.preventDefault();
    setMensaje(null);
    setGuardando(true);
    try {
      await api.post("/ordenes-compra/", {
        proveedor_id: proveedorId,
        sucursal_id: sucursalId,
        items: items.map((it) => ({
          producto_id: it.producto_id,
          cantidad: Number(it.cantidad),
          precio_unitario: Number(it.precio_unitario),
        })),
      });
      setModalAbierto(false);
      setProveedorId("");
      setSucursalId("");
      setItems([{ ...ITEM_VACIO }]);
      cargar();
    } catch (err) {
      setMensaje(extraerError(err, "No se pudo crear la orden"));
    } finally {
      setGuardando(false);
    }
  }

  async function recibir(id: string) {
    try {
      await api.post(`/ordenes-compra/${id}/recibir`);
      cargar();
    } catch (err) {
      alert(extraerError(err, "No se pudo recibir la orden"));
    }
  }

  async function cancelar(id: string) {
    try {
      await api.post(`/ordenes-compra/${id}/cancelar`);
      cargar();
    } catch (err) {
      alert(extraerError(err, "No se pudo cancelar la orden"));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🧾 Órdenes de compra</h1>
        <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
          + Nueva orden
        </button>
      </div>

      <DataTable
        columns={[
          { header: "Proveedor", accessor: (o: OrdenCompra) => nombreProveedor(o.proveedor_id) },
          { header: "Sucursal", accessor: (o: OrdenCompra) => nombreSucursal(o.sucursal_id) },
          { header: "Total", accessor: (o: OrdenCompra) => `S/ ${o.total}` },
          {
            header: "Estado",
            accessor: (o: OrdenCompra) => (
              <span className={`badge badge-${o.estado}`}>
                {EMOJI_ESTADO[o.estado]} {o.estado}
              </span>
            ),
          },
          {
            header: "Acciones",
            accessor: (o: OrdenCompra) =>
              o.estado === "pendiente" ? (
                <div className="table-actions">
                  <button className="btn btn-ghost btn-sm" type="button" onClick={() => recibir(o.id)}>
                    Recibir
                  </button>
                  <button className="btn btn-danger btn-sm" type="button" onClick={() => cancelar(o.id)}>
                    Cancelar
                  </button>
                </div>
              ) : (
                "—"
              ),
          },
        ]}
        data={ordenes}
        keyField={(o) => o.id}
        emptyMessage="Todavía no hay órdenes de compra."
      />

      {modalAbierto && (
        <Modal title="Nueva orden de compra" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crearOrden}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Proveedor</span>
              <select value={proveedorId} onChange={(e) => setProveedorId(e.target.value)} required>
                <option value="">Selecciona un proveedor</option>
                {proveedores.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.razon_social}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Sucursal destino</span>
              <select value={sucursalId} onChange={(e) => setSucursalId(e.target.value)} required>
                <option value="">Selecciona una sucursal</option>
                {sucursales.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>
            </label>

            <p className="field-group-label">Productos</p>
            {items.map((item, index) => (
              <div className="item-row" key={index}>
                <select
                  value={item.producto_id}
                  onChange={(e) => actualizarItem(index, "producto_id", e.target.value)}
                  required
                >
                  <option value="">Producto</option>
                  {productos.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.nombre}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  min="1"
                  placeholder="Cantidad"
                  value={item.cantidad}
                  onChange={(e) => actualizarItem(index, "cantidad", e.target.value)}
                  required
                />
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Precio"
                  value={item.precio_unitario}
                  onChange={(e) => actualizarItem(index, "precio_unitario", e.target.value)}
                  required
                />
                {items.length > 1 && (
                  <button
                    type="button"
                    className="btn-icon"
                    onClick={() => quitarItem(index)}
                    aria-label="Quitar producto"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button type="button" className="btn btn-ghost btn-sm" onClick={agregarItem}>
              + Agregar producto
            </button>

            <div style={{ marginTop: 16 }}>
              <button className="btn btn-primary" type="submit" disabled={guardando}>
                {guardando ? "Guardando..." : "Crear orden"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
