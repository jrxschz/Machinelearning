import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By

# Aeropuertos que vamos a buscar
aeropuertos = [
    "MAD", "BCN", "AGP", "ALC", "VLC", "SVQ", "BIO", "SCQ", "LCG", "VGO",
    "OVD", "SDR", "EAS", "VIT", "PNA", "RJL", "ZAZ", "GRO", "REU", "RMU",
    "LEI", "GRX", "XRY", "ODB", "BJZ", "VLL", "LEN", "RGS", "SLM", "CDT",
    "PMI", "IBZ", "MAH", "LPA", "TFS", "TFN", "ACE", "FUE", "SPC", "GMZ",
    "VDE", "MLN",
]

# Mes que vamos a buscar (noviembre de 2026, que tiene 30 días)
anio = 2026
mes = 11
dias_mes = 30


# Recibe el texto de un vuelo y devuelve una lista con sus datos
def leer_vuelo(texto):
    lineas = texto.split("\n")

    salida = lineas[0]
    llegada = lineas[2]

    # Si el vuelo llega al día siguiente, Google pone "+1" en la línea 3
    # y todo lo demás baja una línea
    if lineas[3].startswith("+"):
        lineas.pop(3)

    aerolinea = lineas[3]
    duracion = lineas[4]
    escalas = lineas[6]

    # El CO2 y el precio no siempre están en la misma línea, así que los buscamos
    co2 = ""
    precio = ""
    for linea in lineas:
        if "CO2e" in linea and co2 == "":
            co2 = linea
        if "€" in linea:
            precio = linea

    return [salida, llegada, aerolinea, duracion, escalas, co2, precio]


# Crear el CSV y escribir la primera fila (los nombres de las columnas)
archivo = open("vuelos.csv", "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["fecha", "origen", "destino", "salida", "llegada",
                   "aerolinea", "duracion", "escalas", "co2", "precio"])

# Abrir Chrome y rechazar las cookies
driver = webdriver.Chrome()
driver.get("https://www.google.com/travel/flights?hl=es&gl=ES")
time.sleep(5)
try:
    driver.find_element(By.XPATH, '//button[contains(., "Rechazar todo")]').click()
except:
    pass  # si no sale el botón, seguimos

# Buscar cada día, cada origen y cada destino
for dia in range(1, dias_mes + 1):
    fecha = f"{anio}-{mes}-{dia:02d}"   # ejemplo: 2026-11-01

    for origen in aeropuertos:
        for destino in aeropuertos:
            if origen == destino:
                continue  # no buscamos MAD -> MAD

            url = f"https://www.google.com/travel/flights?hl=es&gl=ES&q=Flights%20from%20{origen}%20to%20{destino}%20on%20{fecha}%20oneway"
            driver.get(url)
            time.sleep(random.uniform(3, 7))  # esperar a que cargue (y que Google no nos bloquee)

            # Pulsar "Mostrar más vuelos" si existe
            try:
                driver.find_element(By.XPATH, '//button[contains(., "más vuelos")]').click()
                time.sleep(3)
            except:
                pass

            # Coger todos los elementos de la lista de vuelos
            elementos = driver.find_elements(By.XPATH, '//ul/li')

            for elemento in elementos:
                texto = elemento.text

                # Si no tiene precio, no es un vuelo
                if "€" not in texto:
                    continue

                datos = leer_vuelo(texto)
                fila = [fecha, origen, destino] + datos
                escritor.writerow(fila)
                print(fila)

            archivo.flush()  # guardar en el disco lo que llevamos

archivo.close()
driver.quit()
