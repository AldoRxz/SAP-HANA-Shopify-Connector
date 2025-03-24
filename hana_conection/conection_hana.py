from hdbcli import dbapi
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de SAP HANA
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT", 0)),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

try:
    # Conectar a SAP HANA
    connection = dbapi.connect(**HANA_CONFIG)
    print("✅ Conexión exitosa a SAP HANA")

    # Crear cursor
    cursor = connection.cursor()

    # Consulta de prueba (obtener las primeras 5 órdenes de venta)
    query = "SELECT * FROM \"SBO_MANIJAUTO\".\"OITM\" LIMIT 5"

    cursor.execute(query)

    # Obtener resultados
    results = cursor.fetchall()
    for row in results:
        print(row)

    # Cerrar conexión
    connection.close()

except Exception as e:
    print(f"❌ Error conectando a SAP HANA: {e}")
