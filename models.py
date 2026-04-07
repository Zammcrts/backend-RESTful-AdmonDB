from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class UsuarioIn(BaseModel):
    nombre: str
    email:  str

class PedidoIn(BaseModel):
    usuario_id: int
    total:      float

    @field_validator("total")
    def total_no_negativo(cls, v):
        if v < 0:
            raise ValueError("El total no puede ser negativo.")
        return v

class EventoIn(BaseModel):
    usuario_id:  int
    evento:      str
    fecha:       datetime
    dispositivo: str          
    producto_id: Optional[int] = None

    @field_validator("dispositivo")
    def validar_dispositivo(cls, v):
        if v not in ["web", "mobile"]:
            raise ValueError("dispositivo debe ser 'web' o 'mobile'.")
        return v