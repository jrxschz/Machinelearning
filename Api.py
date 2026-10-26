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

COLUMNAS = ["fecha_consulta", "fecha", "origen", "destino", "salida", "llegada",
            "aerolinea", "duracion", "escalas", "co2", "precio",
            "num_vuelo", "avion", "piernas_cm", "wifi", "enchufes",
            "pantallas", "suele_retrasarse", "equipaje_mano"]


def si_no(condicion):
    return "si" if condicion else "no"


# Extrae los datos de un vuelo del JSON de SerpApi
def leer_vuelo(vuelo):
    tramo = vuelo["flights"][0]
    extras = " ".join(tramo.get("extensions", [])).lower()
    minutos = vuelo["total_duration"]
    escalas = len(vuelo.get("layovers", []))
    co2 = vuelo.get("carbon_emissions", {}).get("this_flight", 0)

    return [
        tramo["departure_airport"]["time"].split()[1],
        vuelo["flights"][-1]["arrival_airport"]["time"].split()[1],
        tramo.get("airline", ""),
        f"{minutos // 60} h {minutos % 60} min",
        "Directo" if escalas == 0 else f"{escalas} escala",
        f"{co2 // 1000} kg CO2e" if co2 else "",
        f"{vuelo['price']} €",
        tramo.get("flight_number", ""),
        tramo.get("airplane", ""),
        tramo.get("legroom", "").replace("cm", "").strip(),
        si_no("wi-fi" in extras),
        si_no("corriente" in extras or "usb" in extras),
        si_no("vídeo" in extras or "pantalla" in extras),
        si_no(tramo.get("often_delayed_by_over_30_min")),
        si_no("equipaje de mano" not in str(vuelo.get("extensions", "")).lower()),
    ]


def buscar_vuelos(origen, destino, fecha):
    params = {
        "engine": "google_flights", "departure_id": origen, "arrival_id": destino,
        "outbound_date": fecha, "type": 2, "currency": "EUR", "hl": "es", "gl": "es",
        "deep_search": "true", "show_hidden": "true", "api_key": API_KEY,
    }
    datos = requests.get("https://serpapi.com/search", params=params).json()
    return datos.get("best_flights", []) + datos.get("other_flights", [])


hoy = date.today()
nuevo = not os.path.exists("vuelos_api.csv")

with open("vuelos_api.csv", "a", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    if nuevo:
        escritor.writerow(COLUMNAS)

    for dia in range(1, dias_a_buscar + 1):
        fecha = (hoy + timedelta(days=dia)).isoformat()
        for origen in aeropuertos:
            for destino in aeropuertos:
                if origen == destino:
                    continue
                for vuelo in buscar_vuelos(origen, destino, fecha):
                    try:
                        fila = [hoy.isoformat(), fecha, origen, destino] + leer_vuelo(vuelo)
                    except (KeyError, IndexError, TypeError):
                        continue
                    escritor.writerow(fila)
                    print(fila)
                archivo.flush()
