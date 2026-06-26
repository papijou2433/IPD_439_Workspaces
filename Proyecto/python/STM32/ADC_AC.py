import serial
import numpy as np
import matplotlib.pyplot as plt
import time

PUERTO = '/dev/ttyACM0'
BAUDIOS = 115200
N_MUESTRAS = 16384
FS = 10000

# Comandos Hexadecimales según callbacks.c
TRIGGER_ADC = b'\x01'
TRIGGER_TEMP = b'\x02'

def leer_temperatura(ser):
    """Envía el comando y lee el valor del ADC procesando el prefijo 'T:'."""
    ser.reset_input_buffer()
    ser.write(TRIGGER_TEMP)
    
    linea = ser.readline().decode('utf-8').strip()
    try:
        # Extraemos el valor numérico quitando el prefijo "T:"
        if linea.startswith("T:"):
            valor_adc = float(linea.replace("T:", ""))
        else:
            valor_adc = float(linea) # Fallback por si llega limpio
            
        # --- CÁLCULO DE TEMPERATURA (STM32L4) ---
        v_sense = (valor_adc * 3.3) / 4095.0
        v30 = 0.76         # Voltaje típico a 30°C
        avg_slope = 0.0025 # Pendiente típica (2.5 mV/°C)
        
        temperatura = ((v_sense - v30) / avg_slope) + 30.0
        return valor_adc, temperatura
    except ValueError:
        return None, None

def capturar_uart(ser):
    """Envía el trigger de señal y captura el buffer completo de datos."""
    datos = np.zeros(N_MUESTRAS)
    muestras_perdidas = 0
    
    ser.reset_input_buffer()
    ser.write(TRIGGER_ADC)
    
    for i in range(N_MUESTRAS):
        linea = ser.readline().decode('utf-8').strip()
        try:
            datos[i] = float(linea)
        except ValueError:
            if i > 0:
                datos[i] = datos[i-1]
            else:
                datos[i] = 0.0
            muestras_perdidas += 1
            
    print(f"Captura completada. Muestras corruptas reparadas: {muestras_perdidas}")
    return datos

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

def graficar_espectro(fft_mag, resolucion_freq, f_fund, thd, sinad, enob, temp_ini, temp_fin):
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
        f"ENOB: {enob:.2f} bits\n"
        f"Temp Ini: {temp_ini:.1f} °C\n"
        f"Temp Fin: {temp_fin:.1f} °C"
    )
    plt.text(0.95, 0.95, texto_resultados, transform=plt.gca().transAxes, 
             fontsize=12, verticalalignment='top', horizontalalignment='right', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    datos_adc = None
    t_ini_val = 0.0
    t_fin_val = 0.0
    
    try:
        with serial.Serial(PUERTO, BAUDIOS, timeout=15) as ser:
            
            # 1. Medir temperatura INICIAL
            print("\n[1/3] Solicitando temperatura inicial...")
            adc_t_ini, t_ini_val = leer_temperatura(ser)
            if adc_t_ini is not None:
                print(f"      > Temperatura Inicial: {t_ini_val:.2f} °C (Raw LSB: {adc_t_ini})")
            else:
                print("      > Error al decodificar la temperatura inicial.")
                
            time.sleep(0.1) 
            
            # 2. Capturar señal de CA
            print("\n[2/3] Iniciando captura de datos de CA (16384 muestras)...")
            datos_adc = capturar_uart(ser)
            
            time.sleep(0.1)
            
            # 3. Medir temperatura FINAL
            print("\n[3/3] Solicitando temperatura final...")
            adc_t_fin, t_fin_val = leer_temperatura(ser)
            if adc_t_fin is not None:
                print(f"      > Temperatura Final: {t_fin_val:.2f} °C (Raw LSB: {adc_t_fin})")
            else:
                print("      > Error al decodificar la temperatura final.")
                
    except Exception as e:
        print(f"\nError crítico de conexión UART: {e}")

    # Procesamiento y visualización
    if datos_adc is not None:
        ceros = np.sum(datos_adc == 0.0)
        amplitud_lsb = np.max(datos_adc) - np.min(datos_adc)
        
        print(f"\n--- DIAGNÓSTICO FÍSICO ---")
        print(f"Amplitud Peak-to-Peak de la onda : {amplitud_lsb} LSB")
        print(f"Muestras perdidas (Caídas a 0.0) : {ceros} muestras")
        
        f_fund, thd, sinad, enob, fft_mag, res_freq = calcular_metricas_ac(datos_adc, FS)
        
        print("\n=== RESULTADOS DE CARACTERIZACIÓN AC ===")
        print(f"Frecuencia Fundamental Detectada : {f_fund:.2f} Hz")
        print(f"THD (Distorsión Armónica Total)  : {thd:.2f} dB")
        print(f"SINAD                            : {sinad:.2f} dB")
        print(f"ENOB (Bits Efectivos)            : {enob:.2f} Bits")
        
        graficar_espectro(fft_mag, res_freq, f_fund, thd, sinad, enob, t_ini_val, t_fin_val)