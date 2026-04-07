from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from database import eventos_collection
from models import EventoIn

router = APIRouter()

# endpoint para registrar un evento en MongoDB
@router.post("/")
async def crear_evento(evento: EventoIn):
    doc = {
        "usuario_id":  evento.usuario_id,
        "evento":      evento.evento,
        "fecha":       evento.fecha,          
        "dispositivo": evento.dispositivo,
    }
    if evento.producto_id is not None:
        doc["producto_id"] = evento.producto_id

    result = await eventos_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return {"msg": "Evento registrado", "data": doc}

# endpoint para análisis: evento más frecuente y total de eventos registrados
@router.get("/analisis")
async def analisis_eventos():
    pipeline = [
        {"$group": {"_id": "$evento", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}},
        {"$limit": 1},
    ]
    resultado = await eventos_collection.aggregate(pipeline).to_list(length=1)
    evento_frecuente = resultado[0]["_id"] if resultado else None
    total = await eventos_collection.count_documents({})

    return {
        "evento_mas_frecuente": evento_frecuente,
        "total_eventos":        total
    }