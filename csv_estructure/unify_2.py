from hdbcli import dbapi
import pandas as pd
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

    # Consulta para obtener los datos combinados
    query = """
        SELECT  
            O."ItemCode",  
            O."SWW",
            O."U_ESTA_PROD",  
            COALESCE(W."OnHand", 0) AS "OnHand",  
            COALESCE(P."Price", 0) AS "Price"  
        FROM "SBO_MANIJAUTO"."OITM" O
        LEFT JOIN "SBO_MANIJAUTO"."OITW" W 
            ON O."ItemCode" = W."ItemCode" 
            AND W."WhsCode" = 'M'
        LEFT JOIN "SBO_MANIJAUTO"."ITM1" P
            ON O."ItemCode" = P."ItemCode" 
            AND P."PriceList" = 1
        WHERE O."validFor" = 'Y'
        AND O."ItemType" = 'I'
        LIMIT 10
    """

    cursor.execute(query)

    # Obtener resultados
    results = cursor.fetchall()

    # Crear DataFrame con nombres de columnas
    df = pd.DataFrame(results, columns=['ItemCode', 'Marca', 'Estado', 'OnHand', 'Price'])

    # Mostrar la tabla de manera visual
    print(df.to_string(index=False))

    # Cerrar conexión
    connection.close()

except Exception as e:
    print(f"❌ Error conectando a SAP HANA: {e}")
