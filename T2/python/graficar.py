import pandas as pd
import numpy as np
import os

# Obtener la ruta exacta de la carpeta donde está este script
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Cargar el CSV (Puedes cambiar a "p1_sin_carga" cuando lo necesites)
nombre_archivo = "p1_sin_carga" 
csv_path = os.path.join(directorio_actual, nombre_archivo + ".csv")

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta:\n{csv_path}")
    print("Asegúrate de que el archivo CSV está en la misma carpeta que este script.")
    exit()

time_col = df.columns[0]
resultados = {}

# Mapeo de los nuevos nombres para los canales
etiquetas_canales = {
    "Channel 0": "Tarea 2 (200 ms)",
    "Channel 1": "Tarea 1 (100 ms)"
}

for channel in df.columns[1:]:
    # Asignar el nuevo nombre usando el diccionario
    nombre_canal = etiquetas_canales.get(channel, channel)
    
    # Filtrar valores nulos para este canal en particular
    df_channel = df[[time_col, channel]].dropna().copy()
    
    # Encontrar los cambios de estado (diferencia entre fila actual y anterior)
    df_channel['state_change'] = df_channel[channel].diff()
    
    # Flanco de subida (inicio del ciclo de la tarea)
    rising_edges = df_channel[df_channel['state_change'] == 1][time_col].values
    
    # Necesitamos al menos 2 flancos para tener 1 periodo
    if len(rising_edges) > 1:
        # Calcular el periodo (tiempo entre un flanco de subida y el siguiente)
        # y multiplicar por 1000 para convertir de segundos a milisegundos (ms)
        periodos_ms = np.diff(rising_edges) * 1000.0
        
        # === REGLA: IGNORAR LAS ÚLTIMAS 2 MEDICIONES ===
        if len(periodos_ms) > 2:
            periodos_ms = periodos_ms[:-2]
        else:
            periodos_ms = np.array([])
            
        if len(periodos_ms) > 0:
            resultados[nombre_canal] = {
                'Media Periodo (ms)': round(np.mean(periodos_ms), 4),
                'Jitter / Desviación (ms)': round(np.std(periodos_ms, ddof=1), 4),
                'Mediciones Consideradas': len(periodos_ms)
            }
        else:
            resultados[nombre_canal] = {
                'Media Periodo (ms)': None,
                'Jitter / Desviación (ms)': None,
                'Mediciones Consideradas': 0
            }
    else:
         resultados[nombre_canal] = {
            'Media Periodo (ms)': None,
            'Jitter / Desviación (ms)': None,
            'Mediciones Consideradas': 0
         }

# Crear un DataFrame con el resultado y presentarlo
df_resultados = pd.DataFrame(resultados).T
print(f"--- Análisis Estadístico: {nombre_archivo}.csv ---")
print(df_resultados.to_string())