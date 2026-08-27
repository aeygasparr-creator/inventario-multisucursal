import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import SucursalesPage from "./pages/SucursalesPage";
import CategoriasPage from "./pages/CategoriasPage";
import ProductosPage from "./pages/ProductosPage";
import InventarioPage from "./pages/InventarioPage";
import ProveedoresPage from "./pages/ProveedoresPage";
import ComprasPage from "./pages/ComprasPage";
import VentasPage from "./pages/VentasPage";
import ReportesPage from "./pages/ReportesPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/sucursales" element={<SucursalesPage />} />
              <Route path="/categorias" element={<CategoriasPage />} />
              <Route path="/productos" element={<ProductosPage />} />
              <Route path="/inventario" element={<InventarioPage />} />
              <Route path="/proveedores" element={<ProveedoresPage />} />
              <Route path="/compras" element={<ComprasPage />} />
              <Route path="/ventas" element={<VentasPage />} />
              <Route path="/reportes" element={<ReportesPage />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
