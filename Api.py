import csv
import os
import requests
from datetime import date, timedelta

API_KEY = "TU_API_KEY_AQUI"

aeropuertos = [
    # España
    "MAD", "BCN", "PMI", "AGP", "ALC", "LPA", "TFS", "TFN", "VLC", "SVQ",
    "IBZ", "BIO", "ACE", "FUE", "SCQ", "MAH", "SPC", "OVD", "VGO", "LCG",
    "GRX", "XRY", "SDR", "ZAZ", "RMU", "GRO", "REU", "EAS", "PNA", "LEI",
    "MLN", "BJZ", "VLL", "LEN", "SLM", "VIT", "RJL", "CDT", "VDE", "GMZ",
    # Europa
    "LHR", "LGW", "STN", "CDG", "ORY", "FRA", "MUC", "BER", "AMS", "FCO",
    "MXP", "VCE", "NAP", "LIS", "OPO", "ZRH", "GVA", "VIE", "BRU", "DUB",
    "CPH", "ARN", "OSL", "HEL", "ATH", "IST", "SAW", "WAW", "PRG", "BUD",
    "OTP", "SOF", "ZAG", "BEG", "KEF", "MLA", "LCA", "EDI", "MAN",
    # América del Norte
    "JFK", "EWR", "LAX", "ORD", "MIA", "ATL", "DFW", "SFO", "BOS", "SEA",
    "LAS", "MCO", "DEN", "IAD", "IAH", "PHL", "YYZ", "YVR", "YUL", "MEX",
    "CUN", "GDL", "MTY",
    # América Latina y Caribe
    "BOG", "MDE", "LIM", "SCL", "EZE", "AEP", "GRU", "GIG", "BSB", "PTY",
    "SJO", "HAV", "PUJ", "SDQ", "UIO", "GYE", "CCS", "MVD", "ASU", "LPB",
    # Oriente Medio y África
    "DXB", "AUH", "DOH", "RUH", "JED", "TLV", "AMM", "CAI", "CMN", "RAK",
    "TUN", "ALG", "JNB", "CPT", "NBO", "ADD", "LOS",
    # Asia y Oceanía
    "HND", "NRT", "KIX", "ICN", "PEK", "PKX", "PVG", "CAN", "HKG", "TPE",
    "SIN", "BKK", "KUL", "CGK", "DPS", "MNL", "SGN", "HAN", "DEL", "BOM",
    "BLR", "SYD", "MEL", "BNE", "AKL"
]
dias_a_buscar = 30


# Extrae los datos de un vuelo del JSON de SerpApi
def leer_vuelo(vuelo):
    tramo = vuelo["flights"][0]  # Nos quedamos con el primer tramo

    # Horas de salida y llegada (vienen como "2026-10-23 07:30")
    salida = tramo["departure_airport"]["time"].split(" ")[1]
    llegada = vuelo["flights"][-1]["arrival_airport"]["time"].split(" ")[1]

    aerolinea = tramo.get("airline", "")
    duracion = f"{vuelo['total_duration'] // 60} h {vuelo['total_duration'] % 60} min"

    # Escalas
    num_escalas = len(vuelo.get("layovers", []))
    escalas = "Directo" if num_escalas == 0 else f"{num_escalas} escala"

    # CO2 y precio
    co2_gramos = vuelo.get("carbon_emissions", {}).get("this_flight", 0)
    co2 = f"{co2_gramos // 1000} kg CO2e" if co2_gramos else ""
    precio = f"{vuelo['price']} €"

    # Detalles del avión
    num_vuelo = tramo.get("flight_number", "")
    avion = tramo.get("airplane", "")
    piernas = tramo.get("legroom", "").replace("cm", "").strip()

    # Extras (Wi-Fi, enchufes, etc.)
    extras = " ".join(tramo.get("extensions", [])).lower()
    wifi = "si" if "wi-fi" in extras else "no"
    enchufes = "si" if "corriente" in extras or "usb" in extras else "no"
    pantallas = "si" if "vídeo" in extras or "pantalla" in extras else "no"
    retrasos = "si" if tramo.get("often_delayed_by_over_30_min") else "no"
    equipaje_mano = "no" if "equipaje de mano" in str(vuelo.get("extensions", "")).lower() else "si"

    return [salida, llegada, aerolinea, duracion, escalas, co2, precio,
            num_vuelo, avion, piernas, wifi, enchufes, pantallas, retrasos, equipaje_mano]


# Preparar el archivo CSV aparte
existia = os.path.exists("vuelos_api.csv")
archivo = open("vuelos_api.csv", "a", newline="", encoding="utf-8")
escritor = csv.writer(archivo)

if not existia:
    escritor.writerow(["fecha_consulta", "fecha", "origen", "destino", "salida", "llegada",
                       "aerolinea", "duracion", "escalas", "co2", "precio",
                       "num_vuelo", "avion", "piernas_cm", "wifi", "enchufes",
                       "pantallas", "suele_retrasarse", "equipaje_mano"])

hoy = date.today()
fecha_consulta = hoy.isoformat()

# Buscar por día, origen y destino
for dia in range(1, dias_a_buscar + 1):
    fecha = (hoy + timedelta(days=dia)).isoformat()

    for origen in aeropuertos:
        for destino in aeropuertos:
            if origen == destino:
                continue

            url = f"https://serpapi.com/search?engine=google_flights&departure_id={origen}&arrival_id={destino}&outbound_date={fecha}&type=2&currency=EUR&hl=es&gl=es&deep_search=true&show_hidden=true&api_key={API_KEY}"
            datos = requests.get(url).json()

            # Juntamos los mejores vuelos y el resto de vuelos
            vuelos = datos.get("best_flights", []) + datos.get("other_flights", [])

            for vuelo in vuelos:
                try:
                    fila = [fecha_consulta, fecha, origen, destino] + leer_vuelo(vuelo)
                    escritor.writerow(fila)
                    print(fila)
                except:
                    continue

            archivo.flush()

archivo.close()
