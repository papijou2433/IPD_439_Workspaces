import serial
import time
import numpy as np
import matplotlib.pyplot as plt
PUERTO = 'COM6' 
BAUDRATE = 115200
DATOS_A_LEER = 40000

com = serial.Serial(port=PUERTO, baudrate=BAUDRATE, timeout=20)

# Enviar el comando
tx_msg = 0x01
com.write(bytes([tx_msg]))
datos_adc = []

# Leer exactamente 16354 líneas
for i in range(DATOS_A_LEER):
    linea = com.readline()
    if linea:
        # Decodificar, quitar espacios/saltos y convertir a entero
        valor = int(linea.decode('utf-8').strip())
        datos_adc.append(valor)
    else:
        print(f"Error: Timeout alcanzado en el dato {i}. Se detuvo la transmisión.")
        break

com.close()
y=np.array(datos_adc)
x=np.arange(len(y))

gain, offset = np.polyfit(x,y,1)
print(f"Ecuación de la recta: y = {gain:.6f}x + {offset:.2f}")
print(f"Pendiente (m): {gain:.6f} LSB / muestra")
print(f"Intersección en Y (Offset b): {offset:.2f} LSB")

plt.plot(x,y,label='Datos ADC',color='blue',alpha=0.4)
plt.xlabel('N° de muestra')
plt.ylabel('valor en uint16_t')

plt.show()
datos = np.array(datos_adc)
# generar histograma y excluir 0 y 2^N
histograma = np.bincount(datos, minlength=4096)
histograma_util = histograma[1:4095]
#print(histograma_util[4000])

N_avg = np.sum(histograma_util) / len(histograma_util)
print(f"Promedio de muestras por código (N_avg): {N_avg:.2f}")
dnl_util = (histograma_util / N_avg) - 1.0
DNL = np.zeros(4096)
DNL[1:4095] = dnl_util
INL = np.zeros(4096)
INL[1:4095] = np.cumsum(dnl_util)
    
# Extraer los errores máximos y mínimos
dnl_max, dnl_min = np.max(DNL[1:4095]), np.min(DNL[1:4095])
inl_max, inl_min = np.max(INL[1:4095]), np.min(INL[1:4095])
print(f"DNL Máximo: +{dnl_max:.3f} LSB / Mínimo: {dnl_min:.3f} LSB")
print(f"INL Máximo: +{inl_max:.3f} LSB / Mínimo: {inl_min:.3f} LSB")