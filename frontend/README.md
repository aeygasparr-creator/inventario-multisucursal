# Mastermind_Core — Panel de Administración

Panel visual en React + TypeScript que consume la API del backend. Estética
de consola oscura en rojo, negro y dorado, con animaciones sutiles (pulso en
los indicadores de estado, elevación al pasar el mouse) para que se sienta
menos estático que un CRUD genérico.

## Cómo levantarlo

1. Asegúrate de que el backend esté corriendo en `http://localhost:8000`
   (ver el README principal, en la raíz del proyecto).

2. Instala las dependencias:
   ```
   npm install
   ```

3. Copia las variables de entorno:
   ```
   copy .env.example .env
   ```
   (en Mac/Linux: `cp .env.example .env`)

4. Levanta el servidor de desarrollo:
   ```
   npm run dev
   ```

5. Abre `http://localhost:5173` — te pedirá iniciar sesión con un usuario
   que ya exista en la API (el mismo que usas en Swagger).

## Estructura

```
src/
├── api/client.ts          # Cliente axios: agrega el JWT automáticamente
├── auth/                  # Contexto de autenticación y ruta protegida
├── components/            # Layout, tabla genérica, modal, tarjeta de stat
├── pages/                 # Una página por sección (sucursales, ventas, etc.)
├── types.ts                # Tipos que reflejan los esquemas del backend
└── index.css                # Tema visual (variables de color, componentes)
```

## Notas de diseño

- El precio de una venta se calcula en el backend a partir del catálogo,
  nunca se envía desde el formulario — el panel solo pide producto y cantidad.
- Las acciones de crear/editar están ocultas según el rol del usuario
  (`admin`, `gerente_sucursal`, `vendedor`), igual que en la API.
- El token JWT se guarda en `localStorage` y se adjunta automáticamente a
  cada petición; si expira, la sesión se cierra sola y vuelve al login.
