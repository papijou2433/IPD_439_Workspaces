import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


PORT = 'COM6'         
BAUDRATE = 115200     
SAMPLES = 40000       
TIMEOUT = 10         
BITS = 12
V_REF = 3.3           # Vref del ADC de la STM32 
V_MAX_IN = 3.2      # Amplitud máxima de la rampa
V_MIN_IN = 0.1      
MAX_CODE = (2**BITS) - 1

def capture_uart_data():
    """Envía el comando de inicio y captura las muestras por UART, ignorando checksums."""
    print(f"Abriendo puerto {PORT} a {BAUDRATE} baudios...")
    adc_data = []
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            # Enviar byte 0x01 para iniciar TIM2 y la conversión ADC
            print("Enviando comando de inicio (0x01)...")
            ser.write(b'\x01')
            
            print(f"Recibiendo {SAMPLES} muestras. Esto tomará unos segundos...")
            lines_received = 0
            
            while lines_received < SAMPLES:
                line = ser.readline()
                if not line:
                    print("Timeout alcanzado antes de recibir todas las muestras.")
                    break
                
                try:
                    decoded_line = line.decode('utf-8').strip()
                    # Ignorar las tramas de temperatura provenientes de ADC1/TIM3
                    if decoded_line and not decoded_line.startswith('T:'):
                        adc_data.append(int(decoded_line))
                        lines_received += 1
                except ValueError:
                    # Ignorar líneas corruptas o que no se puedan convertir a entero
                    pass

    except serial.SerialException as e:
        print(f"Error de comunicación serial: {e}")
        return None

    return np.array(adc_data)


def analyze_and_plot_with_linearity(adc_data):
    """Calcula errores estáticos (Offset/Ganancia) y métricas de linealidad (DNL/INL)."""
    if len(adc_data) == 0:
        print("No hay datos para analizar.")
        return

    adc_sorted = np.sort(adc_data)
    v_in_array = np.linspace(V_MIN_IN, V_MAX_IN, len(adc_sorted))
    ideal_slope = MAX_CODE / V_REF
    
    m_real, c_real, r_value, _, _ = stats.linregress(v_in_array, adc_sorted)
    
    offset_error_lsb = c_real
    gain_error_lsb = (m_real - ideal_slope) * V_REF

    hist, bin_edges = np.histogram(adc_data, bins=np.arange(MAX_CODE + 2))
    
    # Identificar los códigos reales que la rampa alcanzó a estimular
    min_code_hit = max(1, np.min(adc_data))
    max_code_hit = min(MAX_CODE - 1, np.max(adc_data))
    
    active_hits = hist[min_code_hit : max_code_hit + 1]
    
    h_ideal = np.mean(active_hits)
    
    if h_ideal > 0:
        dnl_active = (active_hits / h_ideal) - 1.0
    else:
        dnl_active = np.zeros_like(active_hits)
        
    inl_active = np.cumsum(dnl_active)

    # Crear arreglos completos llenos de NaN para evitar graficar los extremos muertos
    dnl = np.full(MAX_CODE - 1, np.nan)
    inl = np.full(MAX_CODE - 1, np.nan)
    
    # Insertar los resultados calculados en sus posiciones correctas (índice 0 = código 1)
    start_idx = min_code_hit - 1
    end_idx = max_code_hit
    dnl[start_idx:end_idx] = dnl_active
    inl[start_idx:end_idx] = inl_active

    # Métricas máximas (ignorando los NaNs)
    dnl_max = np.nanmax(np.abs(dnl))
    inl_max = np.nanmax(np.abs(inl))

    # ==========================================
    # 3. Reporte en Consola
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
    # 4. Visualización Técnica
    # ==========================================
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1, 1]})
    
    # 4a. Función de transferencia
    ideal_codes = v_in_array * ideal_slope
    real_fit_codes = m_real * v_in_array + c_real
    axes[0].plot(v_in_array, ideal_codes, 'k--', label='Ideal', alpha=0.7)
    axes[0].plot(v_in_array, adc_sorted, 'b.', label='Medición', markersize=2, alpha=0.3)
    axes[0].plot(v_in_array, real_fit_codes, 'r-', label='Ajuste Lineal', linewidth=2)
    axes[0].set_title('Función de Transferencia del ADC')
    axes[0].set_ylabel('Código (LSB)')
    axes[0].legend()
    
    # Eje X para DNL/INL (Códigos del 1 al 4094)
    codes = np.arange(1, MAX_CODE)
    
    # 4b. DNL
    axes[1].plot(codes, dnl, 'g-', linewidth=1)
    axes[1].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[1].set_ylabel('DNL (LSB)')
    axes[1].set_title(f'Differential Non-Linearity (Max: {dnl_max:.2f} LSB)')
    
    # 4c. INL
    axes[2].plot(codes, inl, 'm-', linewidth=1)
    axes[2].axhline(0, color='k', linestyle='--', alpha=0.5)
    axes[2].set_xlabel('Código ADC')
    axes[2].set_ylabel('INL (LSB)')
    axes[2].set_title(f'Integral Non-Linearity (Max: {inl_max:.2f} LSB)')
    
    plt.tight_layout()
    plt.show()
if __name__ == '__main__':
    data = capture_uart_data()
    if data is not None:
        analyze_and_plot_with_linearity(data)