import serial
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

PORT = '/dev/ttyACM0' 
BAUDRATE = 115200
SAMPLES = 16384
FS = 10000
TIMEOUT = 20

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

def obtener_potencia_banda(arreglo_potencia, bin_central, span):
    inicio = max(0, bin_central - span)
    fin = min(len(arreglo_potencia), bin_central + span + 1)
    return np.sum(arreglo_potencia[inicio:fin])

def calcular_metricas_ac(datos, fs):
    N = len(datos)
    datos_ac = datos - np.mean(datos)
    
    ventana = np.blackman(N)
    datos_ac = datos_ac * ventana
    
    fft_vals = np.fft.fft(datos_ac) / N
    fft_mag = 2.0 * np.abs(fft_vals[:N//2]) 
    
    factor_correccion_ventana = N / np.sum(ventana)
    fft_mag = fft_mag * factor_correccion_ventana
    
    potencia = (fft_mag / np.sqrt(2))**2
    
    busqueda_inicio = 5 
    fund_bin = np.argmax(potencia[busqueda_inicio:]) + busqueda_inicio
    frecuencia_fundamental = fund_bin * (fs / N)
    
    span = 5 
    potencia_fundamental = obtener_potencia_banda(potencia, fund_bin, span)
    
    potencia_armonicos = 0.0
    num_armonicos = 9
    
    for i in range(2, num_armonicos + 1):
        harm_bin = fund_bin * i
        if harm_bin < (N // 2):
            potencia_armonicos += obtener_potencia_banda(potencia, harm_bin, span)
            
    potencia_total_ac = np.sum(potencia[3:])
    potencia_ruido = potencia_total_ac - potencia_fundamental - potencia_armonicos
    
    if potencia_ruido <= 0: potencia_ruido = 1e-12 
    if potencia_armonicos <= 0: potencia_armonicos = 1e-12

    thd_db = 10 * np.log10(potencia_armonicos / potencia_fundamental)
    sinad_db = 10 * np.log10(potencia_fundamental / (potencia_ruido + potencia_armonicos))
    enob = (sinad_db - 1.76) / 6.02
    
    return frecuencia_fundamental, thd_db, sinad_db, enob, fft_mag, fs/N

def graficar_espectro(fft_mag, resolucion_freq, f_fund, thd, sinad, enob):
    
    max_amp_lsb = 4095.0 / 2.0 
    fft_mag_norm = np.where(fft_mag == 0, 1e-12, fft_mag) / max_amp_lsb
    fft_db = 20 * np.log10(fft_mag_norm)
    
    frecuencias = np.arange(len(fft_mag)) * resolucion_freq
    
    plt.figure(figsize=(10, 6))
    plt.plot(frecuencias, fft_db, color='blue', linewidth=0.8)
    
    plt.title('Espectro de Frecuencias (FFT) del ADC', fontsize=14)
    plt.xlabel('Frecuencia [Hz]', fontsize=12)
    plt.ylabel('Magnitud [dBFS]', fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.6)
    
    texto_resultados = (
        f"F_in: {f_fund:.2f} Hz\n"
        f"THD: {thd:.2f} dB\n"
        f"SINAD: {sinad:.2f} dB\n"
        f"ENOB: {enob:.2f} bits"
    )
    plt.text(0.95, 0.95, texto_resultados, transform=plt.gca().transAxes, 
             fontsize=12, verticalalignment='top', horizontalalignment='right', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    user_input = input("Ingrese el comando a enviar (ej. 1, 5, 0x05): ").strip()
    
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

    datos_adc,temps = capture_uart_data(command_byte)
    
    if datos_adc is not None and len(datos_adc) > 0:
        ceros = np.sum(datos_adc == 0.0)
        amplitud_lsb = np.max(datos_adc) - np.min(datos_adc)
        
        print("\n" + "="*45)
        print(" DIAGNÓSTICO FÍSICO")
        print("="*45)
        print(f"Amplitud Peak-to-Peak            : {amplitud_lsb} LSB")
        print(f"Muestras perdidas (Caídas a 0.0) : {ceros} muestras")
        print(f"Temperatura Inicial : {temps[0]} °C")
        print(f"Temperatura Final : {temps[1]} °C")
        
        f_fund, thd, sinad, enob, fft_mag, res_freq = calcular_metricas_ac(datos_adc, FS)
        
        print("\n" + "="*45)
        print(" RESULTADOS DE CARACTERIZACIÓN AC")
        print("="*45)
        print(f"Frecuencia Fundamental Detectada : {f_fund:.2f} Hz")
        print(f"THD (Distorsión Armónica Total)  : {thd:.2f} dB")
        print(f"SINAD                            : {sinad:.2f} dB")
        print(f"ENOB (Bits Efectivos)            : {enob:.2f} Bits")
        print("="*45)
        
        graficar_espectro(fft_mag, res_freq, f_fund, thd, sinad, enob)