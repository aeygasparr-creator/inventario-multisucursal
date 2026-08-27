import { createContext, useContext, useState, type ReactNode } from "react";
import api from "../api/client";
import { clearStoredToken, getStoredToken, persistToken } from "./tokenStorage";
import type { Rol } from "../types";

interface AuthUser {
  id: string;
  rol: Rol;
}

interface AuthContextType {
  user: AuthUser | null;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function decodeToken(token: string): AuthUser | null {
  try {
    const payload = token.split(".")[1];
    const normalizado = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = JSON.parse(atob(normalizado));
    return { id: decoded.sub, rol: decoded.rol };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const stored = getStoredToken();
    return stored ? decodeToken(stored) : null;
  });

  async function login(email: string, password: string, remember: boolean) {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    const { data } = await api.post("/auth/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    persistToken(data.access_token, remember);
    setUser(decodeToken(data.access_token));
  }

  function logout() {
    clearStoredToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
