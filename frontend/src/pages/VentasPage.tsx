import { useEffect, useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import type { Producto, Sucursal, Venta } from "../types";

interface ItemForm {
  producto_id: string;
  cantidad: string;
}

const ITEM_VACIO: ItemForm = { producto_id: "", cantidad: "" };

const EMOJI_ESTADO: Record<string, string> = {
  confirmada: "✅",
  anulada: "✕",
};

export default function VentasPage() {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [sucursales, setSucursales] = useState<Sucursal[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [sucursalId, setSucursalId] = useState("");
  const [items, setItems] = useState<ItemForm[]>([{ ...ITEM_VACIO }]);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  async function cargar() {
    const [ventRes, sucRes, prodRes] = await Promise.all([
      api.get<Venta[]>("/ventas/"),
      api.get<Sucursal[]>("/sucursales/"),
      api.get<Producto[]>("/productos/"),
    ]);
    setVentas(ventRes.data);
    setSucursales(sucRes.data);
    setProductos(prodRes.data);
  }

  useEffect(() => {
    cargar();
  }, []);

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

  async function crearVenta(e: FormEvent) {
    e.preventDefault();
    setMensaje(null);
    setGuardando(true);
    try {
      await api.post("/ventas/", {
        sucursal_id: sucursalId,
        items: items.map((it) => ({ producto_id: it.producto_id, cantidad: Number(it.cantidad) })),
      });
      setModalAbierto(false);
      setSucursalId("");
      setItems([{ ...ITEM_VACIO }]);
      cargar();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setMensaje(String(err.response.data.detail));
      } else {
        setMensaje("No se pudo registrar la venta (revisa el stock disponible)");
      }
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">💰 Ventas</h1>
        <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
          + Nueva venta
        </button>
      </div>

      <DataTable
        columns={[
          { header: "Sucursal", accessor: (v: Venta) => nombreSucursal(v.sucursal_id) },
          { header: "Total", accessor: (v: Venta) => `S/ ${v.total}` },
          {
            header: "Estado",
            accessor: (v: Venta) => (
              <span className={`badge badge-${v.estado}`}>
                {EMOJI_ESTADO[v.estado]} {v.estado}
              </span>
            ),
          },
          { header: "Fecha", accessor: (v: Venta) => new Date(v.fecha).toLocaleString("es-PE") },
        ]}
        data={ventas}
        keyField={(v) => v.id}
        emptyMessage="Todavía no hay ventas registradas."
      />

      {modalAbierto && (
        <Modal title="Nueva venta" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crearVenta}>
            {mensaje && <p className="form-error">{mensaje}</p>}
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

            <p className="field-group-label">Productos (el precio se toma del catálogo)</p>
            {items.map((item, index) => (
              <div className="item-row item-row-2" key={index}>
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
                {guardando ? "Registrando..." : "Confirmar venta"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
