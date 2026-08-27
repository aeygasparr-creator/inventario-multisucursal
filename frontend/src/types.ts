export type Rol = "admin" | "gerente_sucursal" | "vendedor";

export interface Sucursal {
  id: string;
  nombre: string;
  ciudad: string;
  direccion: string | null;
  activo: boolean;
}

export interface Categoria {
  id: string;
  nombre: string;
  descripcion: string | null;
}

export interface Producto {
  id: string;
  sku: string;
  nombre: string;
  categoria_id: string;
  precio_unitario: string;
  unidad_medida: string;
  activo: boolean;
}

export interface InventarioItem {
  id: string;
  producto_id: string;
  sucursal_id: string;
  stock_actual: number;
  stock_minimo: number;
}

export interface Proveedor {
  id: string;
  razon_social: string;
  ruc: string;
  contacto: string | null;
  telefono: string | null;
  email: string | null;
  activo: boolean;
}

export interface DetalleOrdenCompra {
  id: string;
  producto_id: string;
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
}

export interface OrdenCompra {
  id: string;
  proveedor_id: string;
  sucursal_id: string;
  usuario_id: string;
  estado: "pendiente" | "recibida" | "cancelada";
  fecha: string;
  total: string;
  detalles: DetalleOrdenCompra[];
}

export interface DetalleVenta {
  id: string;
  producto_id: string;
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
}

export interface Venta {
  id: string;
  sucursal_id: string;
  usuario_id: string;
  estado: "confirmada" | "anulada";
  fecha: string;
  total: string;
  detalles: DetalleVenta[];
}

export interface ProductoMasVendido {
  producto_id: string;
  sku: string;
  nombre: string;
  cantidad_vendida: number;
  monto_vendido: string;
}

export interface VentasPorSucursal {
  sucursal_id: string;
  nombre: string;
  cantidad_ventas: number;
  monto_total: string;
}

export interface VentasPorPeriodo {
  periodo: string;
  cantidad_ventas: number;
  monto_total: string;
}

export interface AlertaStock {
  inventario_id: string;
  producto_id: string;
  producto_nombre: string;
  sku: string;
  sucursal_id: string;
  sucursal_nombre: string;
  stock_actual: number;
  stock_minimo: number;
}

export interface RotacionStock {
  producto_id: string;
  producto_nombre: string;
  sucursal_id: string;
  sucursal_nombre: string;
  stock_actual: number;
  vendido_en_periodo: number;
  indice_rotacion: number | null;
}
