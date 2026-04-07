# Ecommerce API

![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB_Atlas-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)

> Backend RESTful desarrollado con FastAPI que integra MySQL y MongoDB Atlas. Incluye modelo relacional con restricciones de integridad, transacciones explícitas con ROLLBACK, modelado NoSQL con validación de esquema y un endpoint analítico que combina ambas fuentes de datos.

**Materia:** Administración de Bases de Datos — Parcial 2

---

## Estructura del proyecto

```
parcial2/
├── routes/
│   ├── __init__.py
│   ├── usuario.py       # POST /usuarios  · GET /usuarios
│   ├── pedido.py        # POST /pedidos   (transacción explícita)
│   ├── evento.py        # POST /eventos   · GET /eventos/analisis
│   └── dashboard.py     # GET  /dashboard/resumen
├── database.py          # Conexiones MySQL y MongoDB Atlas
├── models.py            # Esquemas Pydantic
├── main.py              # App FastAPI + startup automático
└── requirements.txt
```

---

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar el servidor
uvicorn main:app --reload
```

> Swagger UI disponible en `http://localhost:8000/docs`  
> Las tablas MySQL y la colección MongoDB se crean automáticamente al arrancar.

---

## Librerías utilizadas

| Librería | Para qué se usa |
|---|---|
| `fastapi` | Framework principal para construir la API REST |
| `uvicorn` | Servidor ASGI para ejecutar FastAPI |
| `mysql-connector-python` | Conexión y operaciones con MySQL |
| `motor` | Conexión asíncrona con MongoDB Atlas |
| `pydantic` | Validación de datos en los endpoints |
| `dnspython` | Soporte para la URI `mongodb+srv://` de Atlas |

---

## Base de datos MySQL — `ecommerce_db`

### Tabla `usuarios`
| Campo | Tipo | Restricciones |
|---|---|---|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| nombre | VARCHAR(100) | NOT NULL |
| email | VARCHAR(150) | NOT NULL, UNIQUE |

### Tabla `pedidos`
| Campo | Tipo | Restricciones |
|---|---|---|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| usuario_id | INT | NOT NULL, FOREIGN KEY → usuarios(id) |
| total | DECIMAL(10,2) | NOT NULL, CHECK (total >= 0) |
| descuento_aplicado | DECIMAL(10,2) | NOT NULL, DEFAULT 0 |
| fecha | DATETIME | NOT NULL |

### Tabla `pagos`
| Campo | Tipo | Restricciones |
|---|---|---|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| pedido_id | INT | NOT NULL, FOREIGN KEY → pedidos(id) |
| monto | DECIMAL(10,2) | CHECK (monto > 0) |
| fecha_pago | DATETIME | NOT NULL |

---

## Base de datos MongoDB — `ecommerce_logs`

### Colección `eventos_usuario`

Cada documento es validado con `$jsonSchema` al momento de la inserción:

```json
{
  "usuario_id":  "<int, requerido>",
  "evento":      "<string, requerido>",
  "fecha":       "<ISODate, requerido>",
  "dispositivo": "<string, enum: ['web', 'mobile']>",
  "producto_id": "<int, opcional>"
}
```

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/usuarios` | Crear un usuario |
| `GET` | `/usuarios` | Listar todos los usuarios |
| `POST` | `/pedidos` | Crear pedido + pago en transacción |
| `POST` | `/eventos` | Registrar evento en MongoDB |
| `GET` | `/eventos/analisis` | Evento más frecuente + total |
| `GET` | `/dashboard/resumen` | Resumen integrado MySQL + MongoDB |

---

## Pruebas documentadas

### POST /usuarios
<details>
<summary>Ver prueba</summary>

**Request body:**
```json
{
  "nombre": "Ara",
  "email": "ara.papoi@gmail.com"
}
```
**Response `200`:**
```json
{
  "id": 1,
  "nombre": "Ara",
  "email": "ara.papoi@gmail.com"
}
```
</details>

---

### POST /pedidos — con descuento automático
<details>
<summary>Ver prueba</summary>

**Request body:** (`total > 1000` aplica 10% de descuento automáticamente)
```json
{
  "usuario_id": 1,
  "total": 1500
}
```
**Response `200`:**
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

> El pedido y el pago se insertan dentro de una transacción explícita.  
> Si cualquier INSERT falla se ejecuta ROLLBACK completo, no queda ningún registro.
</details>

---

### POST /eventos — registro en MongoDB
<details>
<summary>Ver prueba</summary>

**Request body:**
```json
{
  "usuario_id": 1,
  "evento": "click_producto",
  "fecha": "2025-06-01T10:30:00",
  "dispositivo": "web",
  "producto_id": 42
}
```
**Response `200`:**
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
</details>

---

### GET /eventos/analisis — agregación MongoDB
<details>
<summary>Ver prueba</summary>

Pipeline usado: `$group → $sort → $limit`

**Response `200`:**
```json
{
  "evento_mas_frecuente": "click_producto",
  "total_eventos": 3
}
```
</details>

---

### GET /dashboard/resumen — integración MySQL + MongoDB
<details>
<summary>Ver prueba</summary>

**Response `200`:**
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

> `ventas` proviene de una consulta SUM y AVG sobre la tabla pedidos en MySQL.  
> `eventos` proviene de una agregación y count_documents en MongoDB Atlas.
</details>
