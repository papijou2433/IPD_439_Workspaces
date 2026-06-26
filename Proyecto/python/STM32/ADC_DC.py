import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ==========================================
# Configuración del Puerto y Parámetros
# ==========================================
PORT = '/dev/ttyACM0'      
BAUDRATE = 115200     
SAMPLES = 40000       
TEMP_SAMPLES = 1     # Coincide con MAX_TEMP_SAMPLES en callbacks.c
TIMEOUT = 12          # Aumentado para dar margen a los 5 segundos del Timer 3 + envío DC
BITS = 12
V_REF = 3.3           # Vref del ADC de la STM32 
V_MAX_IN = 3.1        # Amplitud máxima de la rampa
V_MIN_IN = 0.1*1.05-0.025      
MAX_CODE = (2**BITS) - 1

# ==========================================
# Parámetros del Sensor de Temperatura STM32
# ==========================================
V_30 = 0.76           # Voltaje típico a 30°C (Revisar datasheet, ej: 0.76V)
AVG_SLOPE = 0.0025    # Pendiente en V/°C (Revisar datasheet, ej: 2.5 mV/°C)
TEMP_BASE = 30.0      # Temperatura de referencia para V_30

def adc_to_celsius(raw_val):
    """Convierte el valor RAW del ADC a grados Celsius."""
    v_sense = (raw_val * V_REF) / MAX_CODE
    temp_c = ((v_sense - V_30) / AVG_SLOPE) + TEMP_BASE
    return temp_c

def capture_temperature_burst(ser, expected_samples):
    ser.write(b'\x02')
    
    temps_raw = []
    temps_celsius = []
    start_time = time.time()
    
    while len(temps_raw) < expected_samples:
        # Timeout de seguridad
        if time.time() - start_time > 10:
            print("   [!] Timeout alcanzado esperando datos de temperatura.")
            break
            
        line = ser.readline()
        if line:
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith('T:'):
                    # Extraer el valor después de 'T:'
                    raw_val = int(decoded_line.split(':')[1])
                    temp_c = adc_to_celsius(raw_val)
                    
                    temps_raw.append(raw_val)
                    temps_celsius.append(temp_c)
                    print(f"   Temp :{temp_c:.2f} °C")
            except (ValueError, IndexError):
                pass
                
    return np.array(temps_celsius)

def capture_dc_data(ser, expected_samples):
    ser.write(b'\x01')
    
    adc_data = []
    lines_received = 0
    start_time = time.time()
    
    while lines_received < expected_samples:
        line = ser.readline()
        if not line:
            print("   [!] Timeout alcanzado antes de recibir todas las muestras DC.")
            break
        
        try:
            decoded_line = line.decode('utf-8').strip()
            # Asegurarnos de que no sea basura ni una trama de temperatura retrasada
            if decoded_line and not decoded_line.startswith('T:'):
                val = int(decoded_line)
                adc_data.append(val)
                lines_received += 1
                
                    
        except ValueError:
            pass
            
    print(f"<- Captura DC completada ({len(adc_data)}/{expected_samples} muestras).")
    return np.array(adc_data)

def run_capture_sequence():
    """Ejecuta la secuencia completa: Temp inicial -> Datos DC -> Temp final"""
    print(f"Abriendo puerto {PORT} a {BAUDRATE} baudios...")
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            ser.reset_input_buffer()
            time.sleep(0.5)
            
            #  Medición de temperatura inicial
            initial_temps = capture_temperature_burst(ser, TEMP_SAMPLES)
            
            time.sleep(0.5)
            
            dc_data = capture_dc_data(ser, SAMPLES)
            
            time.sleep(0.5)
            
            final_temps = capture_temperature_burst(ser, TEMP_SAMPLES)
            
            return initial_temps, dc_data, final_temps
            
    except serial.SerialException as e:
        print(f"Error de comunicación serial: {e}")
        return None, None, None


def analyze_and_plot_with_linearity(adc_data):
    """Calcula errores estáticos (Offset/Ganancia) y métricas de linealidad (DNL/INL)."""
    if adc_data is None or len(adc_data) == 0:
        print("No hay datos DC para analizar.")
        return

    adc_sorted = np.sort(adc_data)
    v_in_array = np.linspace(V_MIN_IN, V_MAX_IN, len(adc_sorted))
    ideal_slope = MAX_CODE / V_REF
    
    m_real, c_real, r_value, _, _ = stats.linregress(v_in_array, adc_sorted)
    
    offset_error_lsb = c_real
    gain_error_lsb = (m_real - ideal_slope) * V_REF

    hist, bin_edges = np.histogram(adc_data, bins=np.arange(MAX_CODE + 2))
    
    min_code_hit = max(1, np.min(adc_data))
    max_code_hit = min(MAX_CODE - 1, np.max(adc_data))
    
    active_hits = hist[min_code_hit : max_code_hit + 1]
    
    h_ideal = np.mean(active_hits)
    
    if h_ideal > 0:
        dnl_active = (active_hits / h_ideal) - 1.0
    else:
        dnl_active = np.zeros_like(active_hits)
        
    inl_active = np.cumsum(dnl_active)

    dnl = np.full(MAX_CODE - 1, np.nan)
    inl = np.full(MAX_CODE - 1, np.nan)
    
    start_idx = min_code_hit - 1
    end_idx = max_code_hit
    dnl[start_idx:end_idx] = dnl_active
    inl[start_idx:end_idx] = inl_active

    dnl_max = np.nanmax(np.abs(dnl))
    inl_max = np.nanmax(np.abs(inl))

    # ==========================================
    # Reporte en Consola
    # ==========================================
    print("\n" + "="*45)
    print(" RESULTADOS DE CARACTERIZACIÓN (INCL. DNL/INL)")
    print("="*45)
    print(f"Error de Offset     : {offset_error_lsb:.2f} LSB")
    print(f"Error de Ganancia   : {gain_error_lsb:.2f} LSB")
    print(f"Max DNL             : {dnl_max:.3f} LSB")
    print(f"Max INL             : {inl_max:.3f} LSB")
    print(f"Muestras/Código     : {h_ideal:.1f} (Promedio)")
    print("="*45)

    # ==========================================
    # Visualización Técnica
    # ==========================================
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1, 1]})
    
    ideal_codes = v_in_array * ideal_slope
    real_fit_codes = m_real * v_in_array + c_real
    axes[0].plot(v_in_array, ideal_codes, 'k--', label='Ideal', alpha=0.7)
    axes[0].plot(v_in_array, adc_sorted, 'b.', label='Medición', markersize=2, alpha=0.3)
    axes[0].plot(v_in_array, real_fit_codes, 'r-', label='Ajuste Lineal', linewidth=2)
    axes[0].set_title('Función de Transferencia del ADC')
    axes[0].set_ylabel('Código (LSB)')
    axes[0].legend()
    
    codes = np.arange(1, MAX_CODE)
    
    axes[1].plot(codes, dnl, 'g-', linewidth=1)
    axes[1].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[1].set_ylabel('DNL (LSB)')
    axes[1].set_title(f'Differential Non-Linearity (Max: {dnl_max:.2f} LSB)')
    
    axes[2].plot(codes, inl, 'm-', linewidth=1)
    axes[2].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[2].set_xlabel('Código ADC')
    axes[2].set_ylabel('INL (LSB)')
    axes[2].set_title(f'Integral Non-Linearity (Max: {inl_max:.2f} LSB)')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # 1. Capturar todos los datos secuencialmente
    temps_in_c, dc_data_array, temps_out_c = run_capture_sequence()
    
    # 2. Mostrar resumen de temperaturas
    if temps_in_c is not None and temps_out_c is not None and len(temps_in_c) > 0 and len(temps_out_c) > 0:
        mean_in = np.mean(temps_in_c)
        mean_out = np.mean(temps_out_c)
        
        print("\n" + "="*45)
        print(" RESUMEN DE TEMPERATURAS")
        print("="*45)
        print(f"Temperatura Inicial: {mean_in:.2f} °C")
        print(f"Temperatura Final  : {mean_out:.2f} °C")
        print("="*45)
        
    # 3. Analizar y graficar datos DC
    if dc_data_array is not None and len(dc_data_array) > 0:
        analyze_and_plot_with_linearity(dc_data_array)
    else:
        print("\nError: No se capturaron suficientes datos DC para el análisis.")