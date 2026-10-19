import time
import random
import calendar
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By

# Códigos de los aeropuertos españoles
aeropuertos = [
    "MAD", "BCN", "AGP", "ALC", "VLC", "SVQ", "BIO", "SCQ", "LCG", "VGO",
    "OVD", "SDR", "EAS", "VIT", "PNA", "RJL", "ZAZ", "GRO", "REU", "RMU",
    "LEI", "GRX", "XRY", "ODB", "BJZ", "VLL", "LEN", "RGS", "SLM", "CDT",
    "PMI", "IBZ", "MAH", "LPA", "TFS", "TFN", "ACE", "FUE", "SPC", "GMZ",
    "VDE", "MLN",
]

# Calcular el mes siguiente
hoy = date.today()
if hoy.month == 12:
    anio = hoy.year + 1
    mes = 1
else:
    anio = hoy.year
    mes = hoy.month + 1

# Cuántos días tiene ese mes
dias_mes = calendar.monthrange(anio, mes)[1]

# Abrir Chrome y rechazar las cookies
driver = webdriver.Chrome()
driver.get("https://www.google.com/travel/flights?hl=es&gl=ES")
time.sleep(5)
try:
    driver.find_element(By.XPATH, '//button[contains(., "Rechazar todo")]').click()
except Exception:
    pass

# Buscar cada día del mes, cada origen y cada destino
for dia in range(1, dias_mes + 1):
    fecha = date(anio, mes, dia).isoformat()  # ejemplo: "2026-11-01"
    for origen in aeropuertos:
        for destino in aeropuertos:
            if origen == destino:
                continue
            url = f"https://www.google.com/travel/flights?hl=es&gl=ES&q=Flights%20from%20{origen}%20to%20{destino}%20on%20{fecha}%20oneway"
            driver.get(url)
            time.sleep(random.uniform(3, 7))  # espera para que Google no bloquee
