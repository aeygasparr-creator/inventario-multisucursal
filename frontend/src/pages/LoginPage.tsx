import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import AiCoreIllustration from "../components/AiCoreIllustration";
import { CheckCircleIcon, LockIcon, MailIcon } from "../components/icons";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password, remember);
      navigate("/");
    } catch {
      setError("Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-hero">
        <div className="login-hero-illustration">
          <AiCoreIllustration />
        </div>
        <div className="login-hero-content">
          <div className="login-brand">
            <span className="brand-dot" />
            🧠 Mastermind<span className="brand-accent">_Core</span>
          </div>
          <h1 className="login-hero-title">
            Bienvenido de vuelta al <span>panel de control</span>
          </h1>
          <p className="login-hero-subtitle">
            Gestiona sucursales, inventario, compras y ventas de toda la cadena
            desde un solo lugar, con trazabilidad completa de cada movimiento.
          </p>
          <div className="login-hero-features">
            <div className="login-hero-feature">
              <CheckCircleIcon /> Stock en tiempo real por sucursal
            </div>
            <div className="login-hero-feature">
              <CheckCircleIcon /> Transferencias atómicas, sin stock fantasma
            </div>
            <div className="login-hero-feature">
              <CheckCircleIcon /> Reportes listos para Power BI
            </div>
          </div>
        </div>
        <p className="login-hero-footer">Mastermind_Core — Sistema de Inventario y Ventas Multi-sucursal</p>
      </div>

      <div className="login-form-side">
        <form className="login-card" onSubmit={handleSubmit}>
          <h2 className="login-form-title">Iniciar sesión</h2>
          <p className="login-subtitle">Ingresa tus credenciales para continuar</p>
          {error && <p className="form-error">{error}</p>}

          <label className="field">
            <span>Email</span>
            <div className="input-icon-group">
              <MailIcon className="input-icon" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@empresa.com"
                required
              />
            </div>
          </label>

          <label className="field">
            <span>Contraseña</span>
            <div className="input-icon-group">
              <LockIcon className="input-icon" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            />
            Mantener sesión iniciada en este dispositivo
          </label>

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>

          <p className="login-hint">¿No tienes cuenta? Pide a un administrador que te registre.</p>
        </form>
      </div>
    </div>
  );
}
