import requests
import time
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

# Lista de códigos de productos a subir imágenes
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

# Función para verificar si una imagen ya está en Shopify
def image_already_uploaded(product_id, image_url):
    url = f"{SHOPIFY_BASE_URL}/products/{product_id}.json?fields=images"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            images = response.json().get("product", {}).get("images", [])
            for image in images:
                if image_url in image.get("src", ""):
                    return True
        return False
    except requests.exceptions.RequestException:
        return False

# Función para verificar si una imagen existe en el servidor
def image_exists(image_url):
    try:
        response = requests.get(image_url, stream=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Función para subir imágenes a Shopify
def upload_images(variant_sku):
    product_id = get_product_id(variant_sku)
    if not product_id:
        return

    image_base_url = f"https://www.manijauto.com.mx/imagenes/requeridas2/{variant_sku}"
    images = [f"{image_base_url}.jpg"] + [f"{image_base_url}-{i}.jpg" for i in range(1, 7)]
    
    for image_url in images:
        if not image_exists(image_url):
            print(f"⚠️ Imagen no encontrada: {image_url}, omitiendo...")
            continue
        
        if image_already_uploaded(product_id, image_url):
            print(f"🔹 Imagen ya subida: {image_url}, omitiendo...")
            continue
        
        image_data = {
            "image": {
                "src": image_url
            }
        }
        
        url = f"{SHOPIFY_BASE_URL}/products/{product_id}/images.json"
        print(f"📤 Subiendo imagen {image_url} para el producto {variant_sku}...")

        for _ in range(3):  # Reintentar hasta 3 veces en caso de fallo
            try:
                response = requests.post(url, headers=HEADERS, json=image_data)
                if response.status_code == 201:
                    print(f"✅ Imagen subida correctamente: {image_url}")
                    break
                else:
                    print(f"❌ Error al subir {image_url}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de conexión, reintentando: {e}")
                time.sleep(2)

        time.sleep(1)  # Pequeña pausa entre cada imagen

# Subir imágenes para todos los SKUs
for sku in PRODUCT_CODES:
    upload_images(sku)
    time.sleep(2)  # Evita saturar la API de Shopify

print("✅ Todas las imágenes han sido subidas correctamente.")
