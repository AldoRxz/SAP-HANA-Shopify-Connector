import os
import pandas as pd
from dotenv import load_dotenv
from hdbcli import dbapi

# Cargar las variables de entorno desde el archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de SAP HANA
HANA_CONFIG = {
    'address': os.getenv("HANA_ADDRESS"),
    'port': int(os.getenv("HANA_PORT", 0)),
    'user': os.getenv("HANA_USER"),
    'password': os.getenv("HANA_PASSWORD")
}

# Guardar los datos en un archivo Excel
def save_to_excel(df, filename):
    df.to_excel(filename, index=False)

# Guardar los datos en un archivo JSON
def save_to_json(df, filename):
    df.to_json(filename, orient="records", lines=True)

try:
    # Conectar a SAP HANA
    hana_conn = dbapi.connect(**HANA_CONFIG)
    hana_cursor = hana_conn.cursor()
    print("✅ Successfully connected to SAP HANA")

    # Consulta de SAP HANA
    hana_query = """
        SELECT  
            O."ItemCode",  
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
    """
    hana_cursor.execute(hana_query)
    hana_results = hana_cursor.fetchall()
    hana_df = pd.DataFrame(hana_results, columns=['ItemCode', 'OnHand', 'Price'])

    # Guardar los datos en un archivo Excel o JSON
    output_filename = "productos_iniciales.xlsx"  # O usa ".json" para JSON

    # Guardar los datos actuales
    save_to_excel(hana_df, output_filename)  # Guardar como Excel
    # save_to_json(hana_df, output_filename)  # O guardar como JSON

    print(f"✅ Datos guardados en el archivo '{output_filename}'.")

    # Cerrar las conexiones
    hana_cursor.close()
    hana_conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
