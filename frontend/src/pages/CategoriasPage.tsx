import { useEffect, useState, type FormEvent } from "react";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import { useAuth } from "../auth/AuthContext";
import type { Categoria } from "../types";

export default function CategoriasPage() {
  const { user } = useAuth();
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function cargar() {
    const { data } = await api.get<Categoria[]>("/categorias/");
    setCategorias(data);
  }

  useEffect(() => {
    cargar();
  }, []);

  async function crear(e: FormEvent) {
    e.preventDefault();
    setGuardando(true);
    setMensaje(null);
    try {
      await api.post("/categorias/", { nombre, descripcion: descripcion || null });
      setModalAbierto(false);
      setNombre("");
      setDescripcion("");
      cargar();
    } catch (err) {
      setMensaje("No se pudo crear la categoría");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🗂️ Categorías</h1>
        {user?.rol === "admin" && (
          <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
            + Nueva categoría
          </button>
        )}
      </div>

      <DataTable
        columns={[
          { header: "Nombre", accessor: (c: Categoria) => c.nombre },
          { header: "Descripción", accessor: (c: Categoria) => c.descripcion || "—" },
        ]}
        data={categorias}
        keyField={(c) => c.id}
        emptyMessage="Todavía no hay categorías registradas."
      />

      {modalAbierto && (
        <Modal title="Nueva categoría" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crear}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Nombre</span>
              <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
            </label>
            <label className="field">
              <span>Descripción (opcional)</span>
              <input value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
            </label>
            <button className="btn btn-primary" type="submit" disabled={guardando}>
              {guardando ? "Guardando..." : "Crear categoría"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
