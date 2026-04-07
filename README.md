# Ecommerce API – Parcial 2
**Nombre:** Edna Samantha Cortes Carrisoza
**Materia:** Administración de Bases de Datos  
**Tecnologías:** FastAPI · MySQL · MongoDB Atlas

---

## Estructura del proyecto

```
parcial2/
├── routes/
│   ├── __init__.py
│   ├── usuario.py     # POST /usuarios  GET /usuarios
│   ├── pedido.py      # POST /pedidos   (transacción explícita)
│   ├── evento.py      # POST /eventos   GET /eventos/analisis
│   └── dashboard.py   # GET  /dashboard/resumen
├── database.py        # Conexión MySQL y MongoDB Atlas
├── models.py          # Esquemas Pydantic
├── main.py            # App FastAPI + startup
└── requirements.txt
```

---

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar el servidor
uvicorn main:app --reload
```

Swagger UI disponible en → `http://localhost:8000/docs`

---

## Librerías utilizadas

| Librería | Versión | Para qué |
|---|---|---|
| fastapi | 0.111.0 | Framework principal de la API |
| uvicorn | 0.29.0 | Servidor ASGI para correr FastAPI |
| mysql-connector-python | 8.3.0 | Conexión a MySQL |
| motor | 3.4.0 | Conexión asíncrona a MongoDB Atlas |
| pydantic | 2.7.1 | Validación de datos en los endpoints |
| dnspython | - | Soporte para URI mongodb+srv:// |

---

## Base de datos MySQL – ecommerce_db

### Tabla `usuarios`
| Campo | Restricción |
|---|---|
| id | PRIMARY KEY, AUTO_INCREMENT |
| nombre | VARCHAR(100), NOT NULL |
| email | VARCHAR(150), NOT NULL, UNIQUE |

### Tabla `pedidos`
| Campo | Restricción |
|---|---|
| id | PRIMARY KEY, AUTO_INCREMENT |
| usuario_id | NOT NULL, FOREIGN KEY → usuarios(id) |
| total | DECIMAL(10,2), NOT NULL, CHECK (total >= 0) |
| descuento_aplicado | DECIMAL(10,2), NOT NULL, DEFAULT 0 |
| fecha | DATETIME, NOT NULL |

### Tabla `pagos`
| Campo | Restricción |
|---|---|
| id | PRIMARY KEY, AUTO_INCREMENT |
| pedido_id | NOT NULL, FOREIGN KEY → pedidos(id) |
| monto | DECIMAL(10,2), CHECK (monto > 0) |
| fecha_pago | DATETIME, NOT NULL |

---

## Base de datos MongoDB – ecommerce_logs

### Colección `eventos_usuario`
Cada documento cumple el siguiente esquema con `$jsonSchema` validator:

```json
{
  "usuario_id":  <int, requerido>,
  "evento":      <string, requerido>,
  "fecha":       <ISODate, requerido>,
  "dispositivo": <string, enum: ["web", "mobile"]>,
  "producto_id": <int, opcional>
}
```

---

## Pruebas documentadas

### 1. POST /usuarios – Crear usuario

**Body:**
```json
{
  "nombre": "Ara",
  "email": "ara.papoi@gmail.com"
}
```

**Respuesta 200:**
```json
{
  "id": 1,
  "nombre": "Ara",
  "email": "ara.papoi@gmail.com"
}
```

---

### 2. POST /pedidos – Crear pedido con transacción

**Body (total > 1000 → descuento 10%):**
```json
{
  "usuario_id": 1,
  "total": 1500
}
```

**Respuesta 200:**
```json
{
  "pedido_id": 1,
  "usuario_id": 1,
  "total": 1500,
  "descuento_aplicado": 150,
  "monto_pagado": 1350,
  "fecha": "2026-04-07T14:18:49.211581"
}
```

> El pedido y el pago se insertan dentro de una **transacción explícita**.  
> Si cualquier INSERT falla → **ROLLBACK** completo, no queda ningún registro.  
> El descuento del 10% se calcula automáticamente cuando `total > 1000`.

---

### 3. POST /eventos – Registrar evento en MongoDB

**Body:**
```json
{
  "usuario_id": 1,
  "evento": "click_producto",
  "fecha": "2025-06-01T10:30:00",
  "dispositivo": "web",
  "producto_id": 42
}
```

**Respuesta 200:**
```json
{
  "msg": "Evento registrado",
  "data": {
    "usuario_id": 1,
    "evento": "click_producto",
    "fecha": "2025-06-01T10:30:00",
    "dispositivo": "web",
    "producto_id": 42,
    "_id": "69d566e2b2b5a1aa3224ade5"
  }
}
```

---

### 4. GET /eventos/analisis – Análisis con agregación MongoDB

Pipeline utilizado: `$group → $sort → $limit`

**Respuesta 200:**
```json
{
  "evento_mas_frecuente": "click_producto",
  "total_eventos": 3
}
```

---

### 5. GET /dashboard/resumen – Endpoint integrado MySQL + MongoDB

**Respuesta 200:**
```json
{
  "ventas": {
    "total_ventas": 1500,
    "promedio_descuento": 150
  },
  "eventos": {
    "evento_mas_frecuente": "click_producto",
    "total_eventos": 3
  }
}
```

> `ventas` proviene de **MySQL** (SUM y AVG sobre la tabla pedidos).  
> `eventos` proviene de **MongoDB Atlas** (agregación + count).