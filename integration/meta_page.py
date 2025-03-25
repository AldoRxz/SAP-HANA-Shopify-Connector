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
    'port': int(os.getenv("MYSQL_PORT", 0)),
    'database': os.getenv("MYSQL_DATABASE"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'charset': os.getenv("MYSQL_CHARSET")
}

# Lista de códigos de productos a subir
PRODUCT_CODES = [
    108956, 5505, 75474, 75475, 75476, 75477, 107257, 60147, 18708, 70305,
    5636, 70959, 98715, 98005, 96592, 96593, 96595, 96596, 96598, 96600,
    96601, 96602, 96604, 96605, 96606, 96609, 96614, 96615, 96617, 96618,
    96622, 96623, 96626, 96628, 96632, 96634, 96635, 96637, 96641, 96642,
    96663, 96683, 96791, 96793, 96794, 96795, 96804, 96824, 96796, 96797,
    33444, 49052, 33430, 33438, 35112, 49050, 49031, 49048, 50766, 49033,
    51140, 51157, 51158, 51166, 51177, 60186, 22077, 50764, 51139, 22079,
    33429, 51127, 51169, 51175, 60348, 50854, 97100, 108854, 108855, 22456,
    92093, 92132, 92134, 93827, 92145, 96640, 96594, 35102, 108632, 108631,
    108112, 108113, 108222, 108620, 108622, 108226, 108228, 108229, 96487,
    96501
]

# Función para obtener el ID del producto en Shopify a partir del SKU
def get_product_id(variant_sku):
    url = f"{SHOPIFY_BASE_URL}/products.json?fields=id,variants&limit=250"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            products = response.json().get("products", [])
            for product in products:
                for variant in product.get("variants", []):
                    if variant.get("sku") == str(variant_sku):
                        return product["id"]
        print(f"⚠️ No se encontró el producto con SKU {variant_sku} en Shopify")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener ID del producto: {e}")
    return None

# Función para agregar metafields a un producto
def add_metafields(variant_sku, metafields):
    product_id = get_product_id(variant_sku)
    if not product_id:
        return
    
    metafields_url = f"{SHOPIFY_BASE_URL}/products/{product_id}/metafields.json"
    
    for metafield in metafields:
        if not metafield["value"] or metafield["value"] == "None":
            continue  # Evita enviar valores vacíos
        
        metafield_data = {"metafield": metafield}
        for _ in range(3):  # Reintentar hasta 3 veces en caso de fallo
            try:
                response = requests.post(metafields_url, headers=HEADERS, json=metafield_data)
                if response.status_code == 201:
                    break
                else:
                    print(f"❌ {variant_sku} → Error al agregar '{metafield['key']}': {response.text}")
            except requests.exceptions.RequestException as e:
                time.sleep(2)

try:
    # Conectar a MySQL
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Consulta SQL filtrando por los códigos de productos
    format_strings = ','.join(['%s'] * len(PRODUCT_CODES))
    query = f"""
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
        WHERE t1.codigo IN ({format_strings})
        ORDER BY t2.Descripcion, t3.maDescripcion, t4.moDescripcion, t5.vDescripcion;
    """
    cursor.execute(query, PRODUCT_CODES)
    results = cursor.fetchall()
    columns = ['codigo', 'parte', 'marca', 'modelo', 'version', 'ano_inicio', 'ano_fin', 'lado']
    df = pd.DataFrame(results, columns=columns)
    
    # Cerrar conexión a MySQL
    cursor.close()
    connection.close()
    
    # Subir los metafields a Shopify
    for _, row in df.iterrows():
        metafields = [
            {"namespace": "custom", "key": key, "value": str(row[key]), "type": "single_line_text_field"} if key not in ['ano_inicio', 'ano_fin'] else
            {"namespace": "custom", "key": key, "value": int(row[key]), "type": "number_integer"}
            for key in ['parte', 'marca', 'modelo', 'version', 'ano_inicio', 'ano_fin', 'lado']
        ]
        add_metafields(row['codigo'], metafields)
        time.sleep(1)

    print("✅ Todos los metafields han sido subidos correctamente.")

except mysql.connector.Error as e:
    print(f"❌ Error conectando a MySQL: {e}")
