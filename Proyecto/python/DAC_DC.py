import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('AD2_workspaces/DAC/rampa_no_buffer.csv')
plt.figure(figsize=(10, 6))
plt.plot(df['Time (s)'], df['Channel 1 (V)'], label='Canal 1 (V)', color='blue')
if 'Channel 2 (V)' in df.columns:
    plt.plot(df['Time (s)'], df['Channel 2 (V)'], label='Canal 2 (V)', color='orange', alpha=0.7)

plt.title('Medición de la Rampa del DAC (Analog Discovery 2)')
plt.xlabel('Tiempo (s)')
plt.ylabel('Voltaje (V)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# 5. Mostrar la gráfica en pantalla (para correr en tu computadora)
plt.show()

# (Opcional) Si en lugar de mostrarla quieres guardarla como imagen, usa:
# plt.savefig('grafica_rampa.png')