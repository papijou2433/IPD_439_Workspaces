import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Cargar el CSV original
nombre = "cpy_fla"
csv_path = nombre + ".csv"
df = pd.read_csv(csv_path)

time_col = df.columns[0]
datos_grafico = []

# Mapeo de los nuevos nombres para los canales
etiquetas_canales = [
    "32 bytes", "64 bytes", "128 bytes", 
    "256 bytes", "512 bytes", "1024 bytes"
]

# Usamos enumerate para saber qué número de canal estamos iterando
for i, channel in enumerate(df.columns[1:]):
    # Asignar el nuevo nombre según el índice, o mantener el original si hay más de 6 columnas
    nombre_canal = etiquetas_canales[i] if i < len(etiquetas_canales) else channel
    
    # Filtrar valores nulos para cada canal específico
    df_channel = df[[time_col, channel]].dropna().copy()
    
    # Encontrar los cambios de estado
    df_channel['state_change'] = df_channel[channel].diff()
    
    # Identificar los flancos de bajada y subida
    falling_edges = df_channel[df_channel['state_change'] == -1][time_col].values
    rising_edges = df_channel[df_channel['state_change'] == 1][time_col].values
    
    if len(rising_edges) > 0 and len(falling_edges) > 0:
        # Asegurarnos de tener ciclos que inicien con un flanco de bajada
        if rising_edges[0] < falling_edges[0]:
            rising_edges = rising_edges[1:]
            
        min_len = min(len(falling_edges), len(rising_edges))
        falling_edges = falling_edges[:min_len]
        rising_edges = rising_edges[:min_len]
        
        # Calcular la duración y pasar a microsegundos
        low_durations = (rising_edges - falling_edges) * 1_000_000
        
        # IGNORAR LAS ÚLTIMAS 2 MEDICIONES
        if len(low_durations) > 2:
            low_durations = low_durations[:-2]
        else:
            low_durations = np.array([])
            
        # Añadir todos los tiempos de este canal a una lista maestra para graficar
        for val in low_durations:
            # Usar el nombre con el tamaño en bytes
            datos_grafico.append({'Tamaño': nombre_canal, 'Duración Apagado (µs)': val})

# 2. Crear un DataFrame con todos los datos consolidados
df_plot = pd.DataFrame(datos_grafico)

# 3. Configurar y construir el gráfico
plt.figure(figsize=(12, 7))

# Crear diagrama de cajas (Boxplot) para ver medianas y cuartiles
# Se actualizó el eje x para que tome la columna 'Tamaño'
sns.boxplot(x='Tamaño', y='Duración Apagado (µs)', data=df_plot, palette='viridis')

# Superponer los puntos reales con transparencia baja para apreciar la densidad de los datos
sns.stripplot(x='Tamaño', y='Duración Apagado (µs)', data=df_plot, color='black', alpha=0.01, jitter=True)

# 4. Formatear la estética
#plt.title('Distribución de tiempos según tamaño', fontsize=16)
plt.xlabel('Tamaño de Transferencia', fontsize=12) # Etiqueta actualizada
plt.ylabel('Duración de transferencia (µs)', fontsize=12)
plt.ylim(0,100)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# 5. Guardar la imagen en alta resolución
plt.savefig(nombre + '.png', dpi=300)