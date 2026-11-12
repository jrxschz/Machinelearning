import pandas as pd

VUELOS = ["vuelos.csv", "vuelos_nuevos.csv"]
FESTIVOS = "festivos_aeropuertos.csv"
SALIDA = "vuelos_festivos.csv"

# 1. Unir los dos CSV de vuelos (mismas columnas). Las filas corruptas se descartan.
vuelos = pd.concat(
    [pd.read_csv(f, on_bad_lines="skip").assign(fuente=f) for f in VUELOS],
    ignore_index=True,
)
antes = len(vuelos)
vuelos = vuelos.drop_duplicates(subset=[c for c in vuelos.columns if c != "fuente"])
print(f"Vuelos: {antes} filas, {antes - len(vuelos)} duplicadas eliminadas -> {len(vuelos)}")

vuelos["dias_antelacion"] = (
    pd.to_datetime(vuelos["fecha"]) - pd.to_datetime(vuelos["fecha_consulta"])
).dt.days

# 2. Festivos: se cruzan por fecha del vuelo con el aeropuerto de origen y el de destino.
fest = pd.read_csv(FESTIVOS, encoding="utf-8-sig")
comunes = ["fecha", "dia_semana", "es_fin_de_semana"]  # no dependen del aeropuerto
por_aeropuerto = [c for c in fest.columns if c not in comunes + ["aeropuerto"]]

calendario = fest[comunes].drop_duplicates("fecha")
origen = fest[["fecha", "aeropuerto"] + por_aeropuerto].rename(
    columns={"aeropuerto": "origen", **{c: f"origen_{c}" for c in por_aeropuerto}}
)
destino = fest[["fecha", "aeropuerto"] + por_aeropuerto].rename(
    columns={"aeropuerto": "destino", **{c: f"destino_{c}" for c in por_aeropuerto}}
)

df = (
    vuelos.merge(calendario, on="fecha", how="left")
    .merge(origen, on=["fecha", "origen"], how="left")
    .merge(destino, on=["fecha", "destino"], how="left")
)

sin_festivo = df["origen_es_festivo"].isna() | df["destino_es_festivo"].isna()
print(f"Filas sin datos de festivos: {sin_festivo.sum()}")

df.to_csv(SALIDA, index=False, encoding="utf-8-sig")
print(f"Guardadas {len(df)} filas y {df.shape[1]} columnas en {SALIDA}")
