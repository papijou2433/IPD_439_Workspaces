import serial
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

PORT = '/dev/ttyACM0'      
BAUDRATE = 115200     
SAMPLES = 40000       
TIMEOUT = 45       
BITS = 12
V_REF = 3.3
V_MAX_IN = 3.1 
V_MIN_IN = 0.1*0.95-0.025
MAX_CODE = (2**BITS) - 1

def capture_uart_data(command_byte):
    print(f"Abriendo puerto {PORT} a {BAUDRATE} baudios...")
    adc_data = []
    temps = []
    
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:

            ser.dtr = True
            ser.rts = True
            
            ser.reset_input_buffer()
            time.sleep(0.5) # Pausa más corta, solo para estabilizar buffer
            
            print(f"Enviando comando ({hex(command_byte[0])})...")
            ser.write(command_byte)
            ser.flush()
            
            print(f"Recibiendo temperaturas y {SAMPLES} muestras...")
            lines_received = 0
            
            while lines_received < SAMPLES:
                line = ser.readline()
                if not line:
                    print("Timeout alcanzado antes de recibir todas las muestras.")
                    break
                
                try:
                    decoded_line = line.decode('utf-8').strip()
                    if not decoded_line:
                        continue
                        
                    if '.' in decoded_line:
                        if len(temps) < 2:
                            temps.append(float(decoded_line))
                    else:
                        adc_data.append(int(decoded_line))
                        lines_received += 1
                        
                except ValueError:
                    pass

    except serial.SerialException as e:
        print(f"Error de comunicación serial: {e}")
        return None, None

    return np.array(adc_data), temps

def analyze_and_plot_with_linearity(adc_data, temps):
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

    print("\n" + "="*45)
    print(" RESULTADOS DE CARACTERIZACIÓN (INCL. DNL/INL)")
    print("="*45)
    
    if len(temps) >= 2:
        print(f"Temp. Inicial       : {temps[0]:.2f} °C")
        print(f"Temp. Final         : {temps[1]:.2f} °C")
        print(f"Delta Temp.         : {temps[1] - temps[0]:.2f} °C")
        print("-" * 45)
        
    print(f"Error de Offset     : {offset_error_lsb:.2f} LSB")
    print(f"Error de Ganancia   : {gain_error_lsb:.2f} LSB")
    print(f"Max DNL             : {dnl_max:.3f} LSB")
    print(f"Max INL             : {inl_max:.3f} LSB")
    print(f"Muestras/Código     : {h_ideal:.1f} (Promedio)")
    print("="*45)

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
    user_input = input("Ingrese el comando a enviar para la ESP32 (ej. 1, 5, 0x05): ").strip()
    
    try:
        if user_input.lower().startswith('0x'):
            cmd_int = int(user_input, 16)
        else:
            cmd_int = int(user_input)
            
        if not (1 <= cmd_int <= 8):
            print("Advertencia: El comando ingresado no está en el rango esperado (1-8).")
            
        command_byte = bytes([cmd_int])
        
    except ValueError:
        print("Error: Formato inválido. Debes ingresar un número entero o hexadecimal.")
        sys.exit(1)

    data, temps = capture_uart_data(command_byte)
    
    if data is not None:
        analyze_and_plot_with_linearity(data, temps)