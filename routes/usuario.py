from fastapi import APIRouter, HTTPException
from database import get_mysql_conn
from models import UsuarioIn

router = APIRouter()

# endpoint para crear un usuario
@router.post("/")
def crear_usuario(usuario: UsuarioIn):
    conn = get_mysql_conn()
    cur  = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
            (usuario.nombre, usuario.email)
        )
        conn.commit()
        return {"id": cur.lastrowid, "nombre": usuario.nombre, "email": usuario.email}
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=409, detail="El email ya está registrado.")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# endpoint para listar todos los usuarios
@router.get("/")
def listar_usuarios():
    conn = get_mysql_conn()
    cur  = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM usuarios;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()