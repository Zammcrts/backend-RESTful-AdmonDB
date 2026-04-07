from fastapi import APIRouter, HTTPException
from database import get_mysql_conn
from models import PedidoIn
from datetime import datetime

router = APIRouter()

# endpoint para crear pedido + pago dentro de una transacción explícita
@router.post("/")
def crear_pedido(pedido: PedidoIn):
    # calcular descuento: 10% automático si total > 1000
    descuento  = round(pedido.total * 0.10, 2) if pedido.total > 1000 else 0.0
    monto_pago = round(pedido.total - descuento, 2)
    fecha      = datetime.now()

    conn = get_mysql_conn()
    cur  = conn.cursor(dictionary=True)
    try:
        # verificar que el usuario exista
        cur.execute("SELECT id FROM usuarios WHERE id = %s", (pedido.usuario_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Usuario {pedido.usuario_id} no encontrado.")

        # INSERT pedido
        cur.execute(
            """INSERT INTO pedidos (usuario_id, total, descuento_aplicado, fecha)
               VALUES (%s, %s, %s, %s)""",
            (pedido.usuario_id, pedido.total, descuento, fecha)
        )
        pedido_id = cur.lastrowid

        # INSERT pago
        cur.execute(
            """INSERT INTO pagos (pedido_id, monto, fecha_pago)
               VALUES (%s, %s, %s)""",
            (pedido_id, monto_pago, fecha)
        )

        conn.commit()   # ← COMMIT: ambos registros se guardan juntos
        return {
            "pedido_id":          pedido_id,
            "usuario_id":         pedido.usuario_id,
            "total":              pedido.total,
            "descuento_aplicado": descuento,
            "monto_pagado":       monto_pago,
            "fecha":              fecha
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()  # ← ROLLBACK: si algo falla no queda ningún registro
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()