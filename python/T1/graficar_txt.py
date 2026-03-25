import matplotlib.pyplot as plt

# Nombre de tu archivo de texto
nombre_archivo = 'output_2026-03-24_15-29-52.log'

try:
    # 1. Leer los datos del archivo
    with open(nombre_archivo, 'r') as archivo:
        # Leemos cada línea, quitamos espacios/saltos de línea y lo convertimos a entero
        datos_crudos = [int(linea.strip()) for linea in archivo if linea.strip().isdigit()]
    
    # 2. Convertir los valores crudos del ADC a Voltaje
    # Regla: (Valor_ADC / Resolución_Max) * Voltaje_Max
    voltajes = [(valor / 4095.0) * 3.3 for valor in datos_crudos]
    
    # Creamos un vector para el eje X (Número de muestra)
    muestras = list(range(len(voltajes)))

    # 3. Configurar y mostrar la gráfica
    plt.figure(figsize=(10, 5))
    plt.plot(muestras, voltajes, marker='.', linestyle='-', color='b')
    
    # Personalización de la gráfica
    plt.xlabel('Número de Muestra')
    plt.ylabel('Voltaje (V)')
    plt.ylim(0, 3.5) # Dejamos un pequeño margen arriba de 3.3V
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Ajustar el diseño para que no se corten los textos
    plt.tight_layout()
    
    # Mostrar la gráfica en pantalla
    plt.show()

except FileNotFoundError:
    print(f"Error: No se pudo encontrar el archivo '{nombre_archivo}'.")
    print("Asegúrate de que el archivo esté en la misma carpeta que este script.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")