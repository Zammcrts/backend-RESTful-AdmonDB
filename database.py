import mysql.connector
from motor.motor_asyncio import AsyncIOMotorClient

# ── MySQL ─────────────────────────────────────────────────────────────────────
def get_mysql_conn():
    conn = mysql.connector.connect(
        host     = "localhost",
        port     = 3306,
        user     = "root",
        password = "sanki12",            
        database = "ecommerce_db"
    )
    return conn

# ── MongoDB ───────────────────────────────────────────────────────────────────
MONGO_DETAILS = "mongodb+srv://samcortes480_db_user:theSanki12@cluster0.q2t58oy.mongodb.net/?appName=Cluster0"

mongo_client       = AsyncIOMotorClient(MONGO_DETAILS)
mongo_db           = mongo_client["ecommerce_logs"]
eventos_collection = mongo_db.get_collection("eventos_usuario")