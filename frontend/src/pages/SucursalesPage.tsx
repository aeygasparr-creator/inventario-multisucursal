import { useEffect, useState, type FormEvent } from "react";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import { useAuth } from "../auth/AuthContext";
import type { Sucursal } from "../types";

export default function SucursalesPage() {
  const { user } = useAuth();
  const [sucursales, setSucursales] = useState<Sucursal[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [ciudad, setCiudad] = useState("");
  const [direccion, setDireccion] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function cargar() {
    const { data } = await api.get<Sucursal[]>("/sucursales/");
    setSucursales(data);
  }

  useEffect(() => {
    cargar();
  }, []);

  async function crear(e: FormEvent) {
    e.preventDefault();
    setGuardando(true);
    setMensaje(null);
    try {
      await api.post("/sucursales/", { nombre, ciudad, direccion: direccion || null });
      setModalAbierto(false);
      setNombre("");
      setCiudad("");
      setDireccion("");
      cargar();
    } catch (err) {
      setMensaje("No se pudo crear la sucursal");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🏬 Sucursales</h1>
        {user?.rol === "admin" && (
          <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
            + Nueva sucursal
          </button>
        )}
      </div>

      <DataTable
        columns={[
          { header: "Nombre", accessor: (s: Sucursal) => s.nombre },
          { header: "Ciudad", accessor: (s: Sucursal) => s.ciudad },
          { header: "Dirección", accessor: (s: Sucursal) => s.direccion || "—" },
        ]}
        data={sucursales}
        keyField={(s) => s.id}
        emptyMessage="Todavía no hay sucursales registradas."
      />

      {modalAbierto && (
        <Modal title="Nueva sucursal" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crear}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Nombre</span>
              <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
            </label>
            <label className="field">
              <span>Ciudad</span>
              <input value={ciudad} onChange={(e) => setCiudad(e.target.value)} required />
            </label>
            <label className="field">
              <span>Dirección (opcional)</span>
              <input value={direccion} onChange={(e) => setDireccion(e.target.value)} />
            </label>
            <button className="btn btn-primary" type="submit" disabled={guardando}>
              {guardando ? "Guardando..." : "Crear sucursal"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
