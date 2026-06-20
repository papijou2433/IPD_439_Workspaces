import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

archivo_csv = 'Proyecto/AD2_workspaces/DAC/rampa_no_buffer.csv'
v_ref = 3.3
bits = 12
df = pd.read_csv(archivo_csv)

region_reposo = df[(df['Time (s)'] > -0.05) & (df['Time (s)'] < -0.005)]
v_min_real = region_reposo['Channel 1 (V)'].mean()

datos_rampa = df[(df['Time (s)'] > 0.05) & (df['Time (s)'] < 2.047)]
v_max_real = datos_rampa['Channel 1 (V)'].max()

q_ideal = v_ref / (2**bits)
rango_ideal = v_ref - q_ideal

error_offset_lsb = v_min_real / q_ideal

rango_real = v_max_real - v_min_real
error_ganancia_pct = ((rango_real - rango_ideal) / rango_ideal) * 100

print(f"Voltaje medido Código 0: {v_min_real:.4f} V")
print(f"Voltaje medido Código 4095: {v_max_real:.4f} V")
print(f"Error de Offset: {error_offset_lsb:.2f} LSB")
print(f"Error de Ganancia: {error_ganancia_pct:.4f} %")

y = datos_rampa['Channel 1 (V)'].values
x_tiempo = datos_rampa['Time (s)'].values
gain_t, offset_t = np.polyfit(x_tiempo, y, 1)

print(f"Regresión: y = {gain_t:.4f}x + {offset_t:.4f}")

plt.figure(figsize=(10, 5))
plt.plot(df['Time (s)'], df['Channel 1 (V)'])
plt.axhline(v_min_real, color='green', linestyle='--')
plt.axhline(v_max_real, color='red', linestyle='--')
plt.xlim(-0.5, 2.5)
plt.grid(True, alpha=0.6)
plt.show()