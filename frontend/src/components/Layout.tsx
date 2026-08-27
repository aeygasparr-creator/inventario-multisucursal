import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "🎛️ Panel central", end: true },
  { to: "/sucursales", label: "🏬 Sucursales" },
  { to: "/categorias", label: "🗂️ Categorías" },
  { to: "/productos", label: "📦 Productos" },
  { to: "/inventario", label: "🗃️ Inventario" },
  { to: "/proveedores", label: "🚚 Proveedores" },
  { to: "/compras", label: "🧾 Órdenes de compra" },
  { to: "/ventas", label: "💰 Ventas" },
  { to: "/reportes", label: "📈 Reportes" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-dot" />
          🧠 Mastermind<span className="brand-accent">_Core</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <span className="status-badge">
            <span className="status-dot" /> 🟡 CORE ONLINE
          </span>
          <div className="topbar-user">
            <span className="user-role">{user?.rol}</span>
            <button className="btn btn-ghost" type="button" onClick={logout}>
              Cerrar sesión
            </button>
          </div>
        </header>
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
