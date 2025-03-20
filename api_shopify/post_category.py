import requests
import json
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path, override=True)

# Configuración de la API
SHOP_NAME = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# URL de la API para crear colecciones personalizadas
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/custom_collections.json"

# Cabeceras de autenticación
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

# Datos de la nueva colección (categoría)
data = {
    "custom_collection": {
        "title": "Nueva Categoría",
        "body_html": "<p>Esta es una nueva categoría creada desde la API.</p>",
        "image": {
            "src": ""  # URL de una imagen
        }
    }
}

try:
    print(f"🚀 Creando nueva categoría en: {url}")
    
    # Hacer la solicitud POST
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Verificar la respuesta
    if response.status_code == 201:  # 201 significa "Creado"
        new_category = response.json()
        print("✅ Categoría creada correctamente:")
        print(new_category)
    else:
        print(f"⚠️ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")