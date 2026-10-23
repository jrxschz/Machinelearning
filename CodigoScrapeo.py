import csv
import os
import time
import random
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By


# Aeropuertos que vamos a buscar
aeropuertos = [
    "MAD", "TFS", "PMI", "IBZ", "LPA"
]

# Cuántos días hacia delante vamos a buscar (a partir de mañana)
dias_a_buscar = 30


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


# Despliega un vuelo y devuelve los datos extra que salen al abrirlo
def leer_detalles(elemento):
    # Google solo avisa del equipaje de mano cuando NO está incluido
    if "equipaje de mano" in elemento.get_attribute("innerHTML").lower():
        equipaje_mano = "no"
    else:
        equipaje_mano = "si"

    # Pulsar el botón de "Detalles del vuelo"
    try:
        boton = elemento.find_element(By.XPATH, './/button[contains(@aria-label, "etalles")]')
        driver.execute_script("arguments[0].click();", boton)
        time.sleep(2)
    except:
        return ["", "", "", "", "", "", "", equipaje_mano]

    texto = elemento.text
    num_vuelo = ""
    avion = ""
    piernas = ""

    # Si hay escalas nos quedamos con el primer tramo
    for linea in texto.split("\n"):
        # Ejemplo: "Air Europa · Turista · Boeing 737 · UX 7701"
        partes = linea.split(" · ")
        if len(partes) >= 3 and num_vuelo == "":
            avion = partes[-2]
            num_vuelo = partes[-1]
        # Ejemplo: "Espacio medio para las piernas (76 cm)"
        if "piernas" in linea and "cm" in linea and piernas == "":
            piernas = linea.split("(")[-1].replace("cm)", "").strip()

    texto = texto.lower()
    wifi = "si" if "wi-fi" in texto else "no"
    enchufes = "si" if "corriente" in texto or "usb" in texto else "no"
    pantallas = "si" if "vídeo" in texto or "pantalla" in texto else "no"
    retrasos = "si" if "retrasa" in texto else "no"

    return [num_vuelo, avion, piernas, wifi, enchufes, pantallas, retrasos, equipaje_mano]


# Abrir el CSV para añadir filas al final (sin borrar lo anterior)
# Si el archivo no existía, escribimos primero los nombres de las columnas
existia = os.path.exists("vuelos.csv")
archivo = open("vuelos.csv", "a", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
if not existia:
    escritor.writerow(["fecha_consulta", "fecha", "origen", "destino", "salida", "llegada",
                       "aerolinea", "duracion", "escalas", "co2", "precio",
                       "num_vuelo", "avion", "piernas_cm", "wifi", "enchufes",
                       "pantallas", "suele_retrasarse", "equipaje_mano"])

# Día en que se ejecuta el programa (ejemplo: 2026-10-22)
hoy = date.today()
fecha_consulta = hoy.isoformat()

# Abrir Chrome y rechazar las cookies
driver = webdriver.Chrome()
driver.get("https://www.google.com/travel/flights?hl=es&gl=ES")
time.sleep(5)
try:
    driver.find_element(By.XPATH, '//button[contains(., "Rechazar todo")]').click()
except:
    pass  # si no sale el botón, seguimos

# Buscar cada día, cada origen y cada destino
for dia in range(1, dias_a_buscar + 1):
    fecha = (hoy + timedelta(days=dia)).isoformat()   # ejemplo: 2026-10-23

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

                # Si algún vuelo viene raro, lo saltamos en vez de parar el programa
                try:
                    datos = leer_vuelo(texto)
                    detalles = leer_detalles(elemento)
                except:
                    continue

                fila = [fecha_consulta, fecha, origen, destino] + datos + detalles
                escritor.writerow(fila)
                print(fila)

            archivo.flush()  # guardar en el disco lo que llevamos

archivo.close()
driver.quit()
