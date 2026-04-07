from fastapi import APIRouter, HTTPException
from database import get_mysql_conn, eventos_collection

router = APIRouter()

# endpoint analítico integrado: datos desde MySQL y MongoDB 
@router.get("/resumen")
async def dashboard_resumen():
    try:
        # ── MySQL: total acumulado de ventas y promedio de descuento ──────────
        conn = get_mysql_conn()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                COALESCE(SUM(total), 0)              AS total_ventas,
                COALESCE(AVG(descuento_aplicado), 0) AS promedio_descuento
            FROM pedidos;
        """)
        stats = cur.fetchone()
        cur.close()
        conn.close()

        # ── MongoDB: evento más frecuente y total de eventos ──────────────────
        pipeline = [
            {"$group": {"_id": "$evento", "count": {"$sum": 1}}},
            {"$sort":  {"count": -1}},
            {"$limit": 1},
        ]
        top              = await eventos_collection.aggregate(pipeline).to_list(length=1)
        total_eventos    = await eventos_collection.count_documents({})
        evento_frecuente = top[0]["_id"] if top else None

        # ── Respuesta final ───────────────────────────────────────────────────
        return {
            "ventas": {
                "total_ventas":       float(stats["total_ventas"]),
                "promedio_descuento": round(float(stats["promedio_descuento"]), 2)
            },
            "eventos": {
                "evento_mas_frecuente": evento_frecuente,
                "total_eventos":        total_eventos
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))