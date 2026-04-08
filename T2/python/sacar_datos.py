import pandas as pd
import numpy as np

# Cargar el CSV
csv_path = "dma_ram.csv"

df = pd.read_csv(csv_path)

time_col = df.columns[0]
resultados = {}

for channel in df.columns[1:]:
    # Filtrar valores nulos para este canal en particular
    df_channel = df[[time_col, channel]].dropna().copy()
    
    # Encontrar los cambios de estado (diferencia entre fila actual y anterior)
    df_channel['state_change'] = df_channel[channel].diff()
    
    # Flanco de bajada (empieza el estado bajo / se apaga: pasa a ser 0)
    falling_edges = df_channel[df_channel['state_change'] == -1][time_col].values
    
    # Flanco de subida (termina el estado bajo / se enciende: pasa a ser 1)
    rising_edges = df_channel[df_channel['state_change'] == 1][time_col].values
    
    if len(rising_edges) > 0 and len(falling_edges) > 0:
        # Si el primer evento es una subida, significa que la captura empezó con la señal apagada.
        # Ignoramos esa primera subida para medir solo ciclos completos (bajada -> subida).
        if rising_edges[0] < falling_edges[0]:
            rising_edges = rising_edges[1:]
            
        # Emparejar los flancos cortando ambas listas a la longitud de la más corta
        min_len = min(len(falling_edges), len(rising_edges))
        falling_edges = falling_edges[:min_len]
        rising_edges = rising_edges[:min_len]
        
        # Calcular la duración de cada estado de apagado y CONVERTIR A MICROSEGUNDOS (* 1,000,000)
        low_durations = (rising_edges - falling_edges) * 1_000_000
        
        # === REGLA: IGNORAR LAS ÚLTIMAS 2 MEDICIONES ===
        if len(low_durations) > 2:
            low_durations = low_durations[:-2]
        else:
            # Si hay 2 o menos mediciones, al quitar 2 nos quedamos sin nada
            low_durations = np.array([])
            
        if len(low_durations) > 0:
            resultados[channel] = {
                'Media (µs)': np.mean(low_durations),
                'Desviación Estándar (µs)': np.std(low_durations, ddof=1), # ddof=1 para muestra estadística
                'Mediciones Consideradas': len(low_durations)
            }
        else:
            resultados[channel] = {
                'Media (µs)': None,
                'Desviación Estándar (µs)': None,
                'Mediciones Consideradas': 0
            }
    else:
         resultados[channel] = {
            'Media (µs)': None,
            'Desviación Estándar (µs)': None,
            'Mediciones Consideradas': 0
         }

# Crear un DataFrame con el resultado y presentarlo
df_resultados = pd.DataFrame(resultados).T
print(df_resultados)
