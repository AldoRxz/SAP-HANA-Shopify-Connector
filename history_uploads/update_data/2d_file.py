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

# Función para guardar los datos en un archivo Excel
def save_to_excel(df, filename):
    df.to_excel(filename, index=False)

# Función para guardar los datos en un archivo JSON
def save_to_json(df, filename):
    df.to_json(filename, orient="records", lines=True)

# Función para comparar los datos y obtener las diferencias
def compare_data(old_df, new_df):
    # Fusionamos los dataframes basados en 'ItemCode'
    merged_df = pd.merge(old_df, new_df, on='ItemCode', how='outer', suffixes=('_old', '_new'))
    
    # Verificamos si ha habido cambios en 'OnHand' (stock) o 'Price'
    merged_df['Stock Changed'] = merged_df['OnHand_old'] != merged_df['OnHand_new']
    merged_df['Price Changed'] = merged_df['Price_old'] != merged_df['Price_new']
    
    # Filtramos solo las filas que tengan cambios
    changed_df = merged_df[(merged_df['Stock Changed']) | (merged_df['Price Changed'])]
    
    # Seleccionamos solo las columnas relevantes
    changed_df = changed_df[['ItemCode', 'Price_old', 'OnHand_old', 'Price_new', 'OnHand_new']]
    
    # Renombramos las columnas para claridad
    changed_df.rename(columns={
        'Price_old': 'Old Price',
        'OnHand_old': 'Old OnHand',
        'Price_new': 'New Price',
        'OnHand_new': 'New OnHand'
    }, inplace=True)
    
    return changed_df

try:
    # Cargar el archivo antiguo (productos_iniciales.xlsx)
    old_filename = "productos_iniciales.xlsx"
    if os.path.exists(old_filename):
        old_df = pd.read_excel(old_filename)
    else:
        raise FileNotFoundError(f"El archivo '{old_filename}' no se encontró.")
    
    # Conectar a SAP HANA y obtener los nuevos datos
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
    new_df = pd.DataFrame(hana_results, columns=['ItemCode', 'OnHand', 'Price'])

    # Comparar los datos antiguos con los nuevos
    changed_data = compare_data(old_df, new_df)

    # Guardar el archivo con solo los cambios
    if not changed_data.empty:
        output_filename = "productos_diferentes.xlsx"  # O usa ".json" para JSON
        save_to_excel(changed_data, output_filename)  # Guardar como Excel
        # save_to_json(changed_data, output_filename)  # O guardar como JSON
        print(f"✅ Se ha guardado un archivo con las diferencias en '{output_filename}'.")
    else:
        print("⚠️ No se encontraron cambios en los datos.")

    # Cerrar las conexiones
    hana_cursor.close()
    hana_conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
