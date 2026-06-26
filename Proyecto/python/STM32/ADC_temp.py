import serial
import matplotlib.pyplot as plt

PUERTO = '/dev/ttyACM0' 
BAUDIOS = 115200
COMANDO_TEMP = b'\x02'
NUM_MUESTRAS = 10

V_DDA = 3.3
RESOLUCION_ADC = 4095.0
V_30 = 0.76
AVG_SLOPE = 0.0025

def raw_a_celsius(adc_raw):
    v_sense = (adc_raw * V_DDA) / RESOLUCION_ADC
    temp_c = ((v_sense - V_30) / AVG_SLOPE) + 30.0
    return temp_c

def capturar_temperatura():
    datos_temp_c = []
    try:
        with serial.Serial(PUERTO, BAUDIOS, timeout=7) as ser:
            ser.reset_input_buffer()
            
            print(f"Conectado a {PUERTO}. Solicitando captura...")
            ser.write(COMANDO_TEMP)
            
            print("Recibiendo datos...")
            
            while len(datos_temp_c) < NUM_MUESTRAS:
                linea = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if linea.startswith("T:"):
                    try:
                        valor_raw = int(linea.split(":")[1])
                        temp_c = raw_a_celsius(valor_raw)
                        datos_temp_c.append(temp_c)
                        print(f"Muestra {len(datos_temp_c)}/10 -> {temp_c:.1f} °C")
                    except ValueError:
                        pass
                        
        print("¡Captura completada con éxito!")
        return datos_temp_c

    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def graficar_temperatura(datos):
    tiempo = [i * 0.5 for i in range(len(datos))]
    
    plt.figure(figsize=(8, 5))
    plt.plot(tiempo, datos, marker='o', linestyle='-', color='red', linewidth=2)
    
    plt.title('Evolución de la Temperatura Interna (STM32)', fontsize=14)
    plt.xlabel('Tiempo [Segundos]', fontsize=12)
    plt.ylabel('Temperatura [°C]', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.xticks(tiempo)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    datos_recibidos = capturar_temperatura()
    
    if datos_recibidos and len(datos_recibidos) == NUM_MUESTRAS:
        graficar_temperatura(datos_recibidos)
    else:
        print("No se recibieron todas las muestras esperadas.")