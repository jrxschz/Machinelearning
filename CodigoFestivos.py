
import csv
from datetime import date, timedelta

import holidays

SALIDA = "festivos_aeropuertos.csv"
INICIO = date(2026, 1, 1)
FIN = date(2027, 12, 31)

# código IATA -> (ciudad, código de comunidad autónoma)
AEROPUERTOS = {
    "MAD": ("Madrid", "MD"),
    "BCN": ("Barcelona", "CT"),
    "PMI": ("Palma de Mallorca", "IB"),
    "IBZ": ("Ibiza", "IB"),
    "LPA": ("Gran Canaria", "CN"),
    "TFS": ("Tenerife Sur", "CN"),
    "SVQ": ("Sevilla", "AN"),
    "VLC": ("Valencia", "VC"),
    "AGP": ("Málaga", "AN"),
    "ALC": ("Alicante", "VC"),
    "BIO": ("Bilbao", "PV"),
    "TFN": ("Tenerife Norte", "CN"),
}

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def main():
    años = range(INICIO.year, FIN.year + 1)
    nacionales = holidays.Spain(years=años, language="es")
    filas = []

    for iata, (ciudad, comunidad) in AEROPUERTOS.items():
        festivos = holidays.Spain(subdiv=comunidad, years=años, language="es")

        def no_laborable(d):
            return d.weekday() >= 5 or d in festivos

        # Días festivos ordenados, para calcular la distancia al más cercano
        lista_festivos = sorted(d for d in festivos if INICIO - timedelta(60) <= d <= FIN + timedelta(60))

        d = INICIO
        while d <= FIN:
            ayer, mañana = d - timedelta(1), d + timedelta(1)
            es_festivo = d in festivos
            # Puente: día laborable entre un festivo y un fin de semana
            # (lunes antes de un martes festivo, o viernes después de un jueves festivo)
            es_puente = not no_laborable(d) and (
                (d.weekday() == 0 and mañana in festivos)
                or (d.weekday() == 4 and ayer in festivos)
            )
            # Fin de semana largo: el día forma parte de 3 o más días seguidos sin trabajar
            inicio_bloque = fin_bloque = d
            if no_laborable(d):
                while no_laborable(inicio_bloque - timedelta(1)):
                    inicio_bloque -= timedelta(1)
                while no_laborable(fin_bloque + timedelta(1)):
                    fin_bloque += timedelta(1)
            finde_largo = no_laborable(d) and (fin_bloque - inicio_bloque).days + 1 >= 3

            proximo = next((f for f in lista_festivos if f >= d), None)
            anterior = next((f for f in reversed(lista_festivos) if f <= d), None)

            filas.append({
                "fecha": d.isoformat(),
                "aeropuerto": iata,
                "ciudad": ciudad,
                "comunidad": comunidad,
                "dia_semana": DIAS_SEMANA[d.weekday()],
                "es_fin_de_semana": int(d.weekday() >= 5),
                "es_festivo": int(es_festivo),
                "es_festivo_nacional": int(d in nacionales),
                "nombre_festivo": festivos.get(d, ""),
                "es_puente": int(es_puente),
                "finde_largo": int(finde_largo),
                "dias_hasta_festivo": (proximo - d).days if proximo else "",
                "dias_desde_festivo": (d - anterior).days if anterior else "",
            })
            d += timedelta(1)

    with open(SALIDA, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"Guardadas {len(filas)} filas en {SALIDA}")


if __name__ == "__main__":
    main()
