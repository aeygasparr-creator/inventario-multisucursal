import { useEffect, useState, type FormEvent } from "react";
import axios from "axios";
import api from "../api/client";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import { useAuth } from "../auth/AuthContext";
import type { Proveedor } from "../types";

export default function ProveedoresPage() {
  const { user } = useAuth();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [razonSocial, setRazonSocial] = useState("");
  const [ruc, setRuc] = useState("");
  const [contacto, setContacto] = useState("");
  const [telefono, setTelefono] = useState("");
  const [email, setEmail] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function cargar() {
    const { data } = await api.get<Proveedor[]>("/proveedores/");
    setProveedores(data);
  }

  useEffect(() => {
    cargar();
  }, []);

  function limpiarFormulario() {
    setRazonSocial("");
    setRuc("");
    setContacto("");
    setTelefono("");
    setEmail("");
  }

  async function crear(e: FormEvent) {
    e.preventDefault();
    setGuardando(true);
    setMensaje(null);
    try {
      await api.post("/proveedores/", {
        razon_social: razonSocial,
        ruc,
        contacto: contacto || null,
        telefono: telefono || null,
        email: email || null,
      });
      setModalAbierto(false);
      limpiarFormulario();
      cargar();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setMensaje(String(err.response.data.detail));
      } else {
        setMensaje("No se pudo crear el proveedor");
      }
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🚚 Proveedores</h1>
        {user?.rol === "admin" && (
          <button className="btn btn-primary" type="button" onClick={() => setModalAbierto(true)}>
            + Nuevo proveedor
          </button>
        )}
      </div>

      <DataTable
        columns={[
          { header: "Razón social", accessor: (p: Proveedor) => p.razon_social },
          { header: "RUC", accessor: (p: Proveedor) => p.ruc },
          { header: "Contacto", accessor: (p: Proveedor) => p.contacto || "—" },
          { header: "Teléfono", accessor: (p: Proveedor) => p.telefono || "—" },
        ]}
        data={proveedores}
        keyField={(p) => p.id}
        emptyMessage="Todavía no hay proveedores registrados."
      />

      {modalAbierto && (
        <Modal title="Nuevo proveedor" onClose={() => setModalAbierto(false)}>
          <form onSubmit={crear}>
            {mensaje && <p className="form-error">{mensaje}</p>}
            <label className="field">
              <span>Razón social</span>
              <input value={razonSocial} onChange={(e) => setRazonSocial(e.target.value)} required />
            </label>
            <label className="field">
              <span>RUC</span>
              <input value={ruc} onChange={(e) => setRuc(e.target.value)} required />
            </label>
            <label className="field">
              <span>Contacto (opcional)</span>
              <input value={contacto} onChange={(e) => setContacto(e.target.value)} />
            </label>
            <label className="field">
              <span>Teléfono (opcional)</span>
              <input value={telefono} onChange={(e) => setTelefono(e.target.value)} />
            </label>
            <label className="field">
              <span>Email (opcional)</span>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <button className="btn btn-primary" type="submit" disabled={guardando}>
              {guardando ? "Guardando..." : "Crear proveedor"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
