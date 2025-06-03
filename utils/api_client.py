import requests
import httpx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

url = "https://api.open-meteo.com/v1/forecast"

class CustomNominatim(Nominatim):
    def __init__(self, user_agent):
        super().__init__(user_agent=user_agent)
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"User-Agent": user_agent})

    def geocode(self, query, exactly_one=True, timeout=None):
        # Usar la sesión personalizada para deshabilitar la verificación SSL
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1}
        response = self.session.get(base_url, params=params, timeout=timeout)
        response.raise_for_status()
        return self._parse_json(response.json(), exactly_one)

geolocator = CustomNominatim(user_agent="weather_api")

async def fetch_weather_data(city: str):
    """Obtiene datos meteorológicos para una ciudad usando geocodificación."""
    try:
        location = geolocator.geocode(city)
        if not location:
            raise ValueError(f"No se encontraron coordenadas para '{city}'")
 
        latitude = location.latitude
        longitude = location.longitude
 
    except GeocoderServiceError as e:
        raise Exception(f"Error al obtener coordenadas: {str(e)}")
 
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,rain"
    }

    """Función para obtener los datos de la API externa."""
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return {
                "city": city.title(),
                "latitude": latitude,
                "longitude": longitude,
                "weather_data": {
                    "time": data["hourly"]["time"],
                    "temperature_2m": data["hourly"]["temperature_2m"],
                    "relative_humidity_2m": data["hourly"]["relative_humidity_2m"],
                    "rain": data["hourly"]["rain"]
                }
            }

    except httpx.RequestError as e:
        raise Exception(f"Error de conexión con Open Meteo: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Respuesta inválida de Open Meteo: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")