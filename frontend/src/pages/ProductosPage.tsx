import { useEffect, useState, type FormEvent } from "react";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import { useAuth } from "../auth/AuthContext";
import type { Categoria, Producto } from "../types";

export default function ProductosPage() {
  const { user } = useAuth();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [sku, setSku] = useState("");
  const [nombre, setNombre] = useState("");
  const [categoriaId, setCategoriaId] = useState("");
  const [precio, setPrecio] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function cargar() {
    const [prodRes, catRes] = await Promise.all([
      api.get<Producto[]>("/productos/"),
      api.get<Categoria[]>("/categorias/"),
    ]);
    setProductos(prodRes.data);
    setCategorias(catRes.data);
  }

  useEffect(() => {
    cargar();
  }, []);

  function nombreCategoria(id: string) {
    return categorias.find((c) => c.id === id)?.nombre || "—";
  }

  async function crear(e: FormEvent) {
    e.preventDefault();
    setGuardando(true);
    setMensaje(null);
    try {
      await api.post("/productos/", {
        sku,
        nombre,
        categoria_id: categoriaId,
        precio_unitario: Number(precio),
      });
      setModalAbierto(false);
      setSku("");
      setNombre("");
      setCategoriaId("");
      setPrecio("");
      cargar();
    } catch (err) {
      setMensaje("No se pudo crear el producto (revisa que el SKU no esté repetido)");
    } finally {
      setGuardando(false);
    }
  }

  const puedeCrear = user?.rol === "admin" || user?.rol === "gerente_sucursal";

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">📦 Productos</h1>
        {puedeCrear && (
          <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
            + Nuevo producto
          </button>
        )}
      </div>

      <DataTable
        columns={[
          { header: "SKU", accessor: (p: Producto) => p.sku },
          { header: "Nombre", accessor: (p: Producto) => p.nombre },
          { header: "Categoría", accessor: (p: Producto) => nombreCategoria(p.categoria_id) },
          { header: "Precio", accessor: (p: Producto) => `S/ ${p.precio_unitario}` },
        ]}
        data={productos}
        keyField={(p) => p.id}
        emptyMessage="Todavía no hay productos registrados."
      />

      {modalAbierto && (
        <Modal title="Nuevo producto" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crear}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>SKU</span>
              <input value={sku} onChange={(e) => setSku(e.target.value)} required />
            </label>
            <label className="field">
              <span>Nombre</span>
              <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
            </label>
            <label className="field">
              <span>Categoría</span>
              <select value={categoriaId} onChange={(e) => setCategoriaId(e.target.value)} required>
                <option value="">Selecciona una categoría</option>
                {categorias.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Precio unitario</span>
              <input
                type="number"
                step="0.01"
                min="0"
                value={precio}
                onChange={(e) => setPrecio(e.target.value)}
                required
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={guardando}>
              {guardando ? "Guardando..." : "Crear producto"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
