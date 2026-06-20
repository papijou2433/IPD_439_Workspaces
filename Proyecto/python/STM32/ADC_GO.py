import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


PORT = '/dev/ttyACM0'     
BAUDRATE = 115200     
SAMPLES = 40000       
TIMEOUT = 10         
BITS = 12
V_REF = 3.3           # Vref del ADC de la STM32 
V_MAX_IN = 3.1      # Amplitud máxima de la rampa
V_MIN_IN = 0.14      
MAX_CODE = (2**BITS) - 1

def capture_uart_data():
    """Envía el comando de inicio y captura las muestras por UART, ignorando checksums."""
    print(f"Abriendo puerto {PORT} a {BAUDRATE} baudios...")
    adc_data = []
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            # --- SOLUCIÓN DE SINCRONIZACIÓN ---
            ser.dtr = True
            ser.rts = True
            #print("Esperando 2 segundos a que la ESP32 inicialice...")
            time.sleep(2) 
            
            # Limpiar cualquier basura en el buffer antes de empezar
            ser.reset_input_buffer() 
            # -----------------------------------

            # Enviar byte 0x01 para iniciar la conversión ADC
            print("Enviando comando de inicio (0x01)...")
            ser.write(b'\x01')
            
            print(f"Recibiendo {SAMPLES} muestras. Esto tomará unos segundos...")
            lines_received = 0
            
            while lines_received < SAMPLES:
                line = ser.readline()
                if not line:
                    print(f"Timeout alcanzado. Se recibieron {lines_received} de {SAMPLES} muestras.")
                    break
                
                try:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line and not decoded_line.startswith('T:'):
                        adc_data.append(int(decoded_line))
                        lines_received += 1
                except ValueError:
                    pass

    except serial.SerialException as e:
        print(f"Error de comunicación serial: {e}")
        return None

    return np.array(adc_data)

def analyze_and_plot(adc_data):
    """Calcula los errores de offset y ganancia y genera las gráficas."""
    if len(adc_data) == 0:
        print("No hay datos para analizar.")
        return

    # 1. Ordenar los datos para reconstruir la función de transferencia
    # Asumiendo que la rampa cubrió uniformemente desde V_MIN_IN hasta V_MAX_IN
    adc_sorted = np.sort(adc_data)
    v_in_array = np.linspace(V_MIN_IN, V_MAX_IN, len(adc_sorted))
    # 2. curva total
    ideal_slope = MAX_CODE / V_REF
    ideal_codes = v_in_array * ideal_slope
    
    # 3. Regresión lineal de la medición (Segmento evaluado)
    m_real, c_real, r_value, _, _ = stats.linregress(v_in_array, adc_sorted)
    real_fit_codes = m_real * v_in_array + c_real
    
    # 4. Cálculo de Errores Estandarizados
    # Offset: Desviación en el origen (Vin = 0V)
    offset_error_lsb = c_real
    
    # Ganancia: Diferencia de las pendientes evaluada a fondo de escala (V_REF)
    gain_error_lsb = (m_real - ideal_slope) * V_REF
    
    # Conversión a Voltaje (opcional)
    lsb_volts = V_REF / MAX_CODE
    offset_error_mv = offset_error_lsb * lsb_volts * 1000
    
    print("\n" + "="*40)
    print(" RESULTADOS DE CARACTERIZACIÓN DC")
    print("="*40)
    print(f"Muestras procesadas : {len(adc_data)}")
    print(f"Coeficiente R^2     : {r_value**2:.6f}")
    print(f"Error de Offset     : {offset_error_lsb:.2f} LSB ({offset_error_mv:.2f} mV)")
    print(f"Error de Ganancia   : {gain_error_lsb:.2f} LSB")
    print("="*40)

    # 5. Visualización Técnica (Matplotlib/Seaborn style)
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Gráfico superior: Función de transferencia
    ax1.plot(v_in_array, ideal_codes, 'k--', label='Ideal', alpha=0.7)
    ax1.plot(v_in_array, adc_sorted, 'b.', label='Medición cruda', markersize=2, alpha=0.3)
    ax1.plot(v_in_array, real_fit_codes, 'r-', label='Ajuste Lineal', linewidth=2)
    ax1.set_title('Función de Transferencia del ADC (STM32L476RG)')
    ax1.set_ylabel('Código ADC (LSB)')
    ax1.legend()
    
    # Gráfico inferior: Error Residual (No linealidad total aproximada)
    error_residual = adc_sorted - real_fit_codes
    ax2.plot(v_in_array, error_residual, 'g-', alpha=0.8)
    ax2.axhline(0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Voltaje de Entrada (V)')
    ax2.set_ylabel('Error Residual (LSB)')
    ax2.set_title('Desviación respecto al ajuste lineal')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    data = capture_uart_data()
    if data is not None:
        analyze_and_plot(data)