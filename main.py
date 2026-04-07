from fastapi import FastAPI
from database import get_mysql_conn, mongo_db

from routes.usuario   import router as usuario_router
from routes.pedido    import router as pedido_router
from routes.evento    import router as evento_router
from routes.dashboard import router as dashboard_router

app = FastAPI(
    title       = "Ecommerce API",
    description = "Parcial 2",
    version     = "1.0.0"
)

# ── Startup: crear tablas MySQL y colección MongoDB si no existen ─────────────
@app.on_event("startup")
async def startup():
    # MySQL
    conn = get_mysql_conn()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id     INT          PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            email  VARCHAR(150) NOT NULL UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id                 INT           PRIMARY KEY AUTO_INCREMENT,
            usuario_id         INT           NOT NULL,
            total              DECIMAL(10,2) NOT NULL,
            descuento_aplicado DECIMAL(10,2) NOT NULL DEFAULT 0,
            fecha              DATETIME      NOT NULL,
            CONSTRAINT chk_total         CHECK (total >= 0),
            CONSTRAINT fk_pedido_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id         INT           PRIMARY KEY AUTO_INCREMENT,
            pedido_id  INT           NOT NULL,
            monto      DECIMAL(10,2),
            fecha_pago DATETIME      NOT NULL,
            CONSTRAINT chk_monto      CHECK (monto > 0),
            CONSTRAINT fk_pago_pedido FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
   

    # MongoDB
    existing = await mongo_db.list_collection_names()
    if "eventos_usuario" not in existing:
        await mongo_db.create_collection(
            "eventos_usuario",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["usuario_id", "evento", "fecha", "dispositivo"],
                    "properties": {
                        "usuario_id":  {"bsonType": "int"},
                        "evento":      {"bsonType": "string"},
                        "fecha":       {"bsonType": "date"},
                        "dispositivo": {"bsonType": "string", "enum": ["web", "mobile"]},
                        "producto_id": {"bsonType": ["int", "null"]}
                    }
                }
            }
        )
        print("colección eventos_usuario creada")
    else:
        print("colección eventos_usuario ya existe")

# ── Rutas ─────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"msg": "Ecommerce API funcionando"}

app.include_router(usuario_router,   prefix="/usuarios",  tags=["Usuarios"])
app.include_router(pedido_router,    prefix="/pedidos",   tags=["Pedidos"])
app.include_router(evento_router,    prefix="/eventos",   tags=["Eventos"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])