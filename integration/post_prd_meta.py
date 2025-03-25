import requests
import time
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de Shopify
SHOP_NAME = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOPIFY_BASE_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# Configuración de MySQL
DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT")),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET")
}

# Función para agregar metafields a un producto
def add_metafields(product_id, metafields):
    metafields_url = f"{SHOPIFY_BASE_URL}/products/{product_id}/metafields.json"
    
    for metafield in metafields:
        metafield_data = {"metafield": metafield}
        response = requests.post(metafields_url, headers=HEADERS, json=metafield_data)

        if response.status_code == 201:
            print(f"✅ Metafield '{metafield['key']}' agregado correctamente al producto {product_id}")
        else:
            print(f"❌ Error al agregar '{metafield['key']}' al producto {product_id}: {response.text}")

try:
    # Conectar a MySQL
    connection = mysql.connector.connect(**DB_CONFIG)
    print("✅ Conexión exitosa a MySQL")
    cursor = connection.cursor()

    # Consulta SQL
    query = """
        SELECT 
            t1.codigo AS codigo,
            t2.Descripcion AS parte,
            t3.maDescripcion AS marca,
            t4.moDescripcion AS modelo,
            t5.vDescripcion AS version,
            CAST(t6.Anio AS UNSIGNED) AS ano_inicio,
            CAST(t61.Anio AS UNSIGNED) AS ano_fin,
            lad.lado_description AS lado
        FROM aplicaciones_ap t1
        JOIN descripciones_ap t7 ON t1.codigo = t7.codigo
        LEFT JOIN tiposparte_ap t2 ON t2.Id = t1.tipo_parte
        LEFT JOIN tiposmarca_ap t3 ON t3.IdMarca = t1.id_marca
        LEFT JOIN tiposmodelo_ap t4 ON t4.IdModelo = t1.id_modelo
        LEFT JOIN tiposversion_ap t5 ON t5.IdVersion = t1.id_version
        LEFT JOIN anios t6 ON t6.Id = t1.id_ano_in
        LEFT JOIN anios t61 ON t61.Id = t1.id_ano_fin
        LEFT JOIN lado_ap lad ON lad.id_lado = t1.id_lado
        ORDER BY t2.Descripcion, t3.maDescripcion, t4.moDescripcion, t5.vDescripcion;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    columns = ['codigo', 'parte', 'marca', 'modelo', 'version', 'ano_inicio', 'ano_fin', 'lado']
    df = pd.DataFrame(results, columns=columns)

    # Convertir los años a enteros
    df['ano_inicio'] = df['ano_inicio'].fillna(0).astype(int)
    df['ano_fin'] = df['ano_fin'].fillna(0).astype(int)

    # Cerrar conexión a MySQL
    cursor.close()
    connection.close()
    
    # Simulación de IDs de productos en Shopify (debes reemplazar esto con los IDs reales)
    product_ids = {row['codigo']: 9859403055421 + idx for idx, row in df.iterrows()}

    # Subir los metafields a Shopify
    for _, row in df.iterrows():
        product_id = product_ids.get(row['codigo'])
        if not product_id:
            print(f"⚠️ No se encontró ID de Shopify para el SKU {row['codigo']}")
            continue

        metafields = [
            {"namespace": "global", "key": "parte", "value": row['parte'], "type": "string"},
            {"namespace": "global", "key": "marca", "value": row['marca'], "type": "string"},
            {"namespace": "global", "key": "modelo", "value": row['modelo'], "type": "string"},
            {"namespace": "global", "key": "version", "value": row['version'], "type": "string"},
            {"namespace": "global", "key": "ano_inicio", "value": str(row['ano_inicio']), "type": "integer"},
            {"namespace": "global", "key": "ano_fin", "value": str(row['ano_fin']), "type": "integer"},
            {"namespace": "global", "key": "lado", "value": row['lado'], "type": "string"}
        ]
        add_metafields(product_id, metafields)
        time.sleep(1)  # Evita exceder el límite de Shopify

    print("✅ Todos los metafields han sido subidos correctamente.")

except mysql.connector.Error as e:
    print(f"❌ Error conectando a MySQL: {e}")
