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

# Lista de códigos de productos a eliminar imágenes
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

# Función para eliminar todas las imágenes de un producto
def delete_images(variant_sku):
    product_id = get_product_id(variant_sku)
    if not product_id:
        return
    
    url = f"{SHOPIFY_BASE_URL}/products/{product_id}.json?fields=images"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            images = response.json().get("product", {}).get("images", [])
            if not images:
                print(f"⚠️ No hay imágenes para eliminar en el producto {variant_sku}")
                return
            
            for image in images:
                image_id = image.get("id")
                delete_url = f"{SHOPIFY_BASE_URL}/products/{product_id}/images/{image_id}.json"
                delete_response = requests.delete(delete_url, headers=HEADERS)
                
                if delete_response.status_code == 200:
                    print(f"✅ Imagen {image_id} eliminada para el producto {variant_sku}")
                else:
                    print(f"❌ Error al eliminar imagen {image_id}: {delete_response.text}")
                time.sleep(1)  # Pausa para evitar saturar la API
        else:
            print(f"❌ No se pudieron obtener imágenes para {variant_sku}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al eliminar imágenes: {e}")

# Eliminar imágenes de todos los productos
for sku in PRODUCT_CODES:
    delete_images(sku)
    time.sleep(2)  # Evita saturar la API de Shopify

print("✅ Todas las imágenes han sido eliminadas correctamente.")
