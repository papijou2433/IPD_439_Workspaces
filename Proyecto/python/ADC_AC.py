import serial
import time
import numpy as np
import matplotlib.pyplot as plt

PUERTO = 'COM6'
BAUDIOS = 115200
N_MUESTRAS = 16384
FS = 10000
TRIGGER = b'\x01'

def capturar_uart():
    datos = np.zeros(N_MUESTRAS)
    try:
        with serial.Serial(PUERTO, BAUDIOS, timeout=15) as ser:
            ser.reset_input_buffer()
            
            ser.write(TRIGGER)
            
            for i in range(N_MUESTRAS):
                #gracias gemini
                linea = ser.readline().decode('utf-8').strip()
                if linea.isdigit():
                    datos[i] = float(linea)
                else:
                    datos[i] = 0.0
                    
            print("Captura completada")
            return datos
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def calcular_metricas_ac(datos, fs):
    N = len(datos)
    
    datos_ac = datos - np.mean(datos)
    
    fft_vals = np.fft.fft(datos_ac) / N
    fft_mag = 2.0 * np.abs(fft_vals[:N//2]) 
    
    potencia = (fft_mag / np.sqrt(2))**2
    
    fund_bin = np.argmax(potencia)
    potencia_fundamental = potencia[fund_bin]
    frecuencia_fundamental = fund_bin * (fs / N)
    
    potencia_armonicos = 0.0
    num_armonicos = 9
    
    for i in range(2, num_armonicos + 1):
        harm_bin = fund_bin * i
        if harm_bin < (N // 2):
            potencia_armonicos += potencia[harm_bin]
            
    potencia_total_ac = np.sum(potencia)
    potencia_ruido = potencia_total_ac - potencia_fundamental - potencia_armonicos
    
    if potencia_ruido <= 0: potencia_ruido = 1e-12 
    if potencia_armonicos <= 0: potencia_armonicos = 1e-12

    thd_db = 10 * np.log10(potencia_armonicos / potencia_fundamental)
    sinad_db = 10 * np.log10(potencia_fundamental / (potencia_ruido + potencia_armonicos))
    enob = (sinad_db - 1.76) / 6.02
    
    return frecuencia_fundamental, thd_db, sinad_db, enob, fft_mag, fs/N

def graficar_espectro(fft_mag, resolucion_freq, f_fund, thd, sinad, enob):
    fft_mag = np.where(fft_mag == 0, 1e-12, fft_mag)
    fft_db = 20 * np.log10(fft_mag)
    
    frecuencias = np.arange(len(fft_mag)) * resolucion_freq
    
    plt.figure(figsize=(10, 6))
    plt.plot(frecuencias, fft_db, color='blue', linewidth=0.8)
    
    plt.title('Espectro de Frecuencias (FFT) del ADC - STM32', fontsize=14)
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

if __name__ == "__main__":
    datos_adc = capturar_uart()
    
    if datos_adc is not None:
        f_fund, thd, sinad, enob, fft_mag, res_freq = calcular_metricas_ac(datos_adc, FS)
        
        print("\n=== RESULTADOS DE CARACTERIZACIÓN AC ===")
        print(f"Frecuencia Fundamental Detectada : {f_fund:.2f} Hz")
        print(f"THD (Distorsión Armónica Total)  : {thd:.2f} dB")
        print(f"SINAD                            : {sinad:.2f} dB")
        print(f"ENOB (Bits Efectivos)            : {enob:.2f} Bits")
        
        graficar_espectro(fft_mag, res_freq, f_fund, thd, sinad, enob)