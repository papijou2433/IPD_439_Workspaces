import serial
import time

PORT = '/dev/ttyACM0'
BAUDRATE = 115200

print(f"Conectando a {PORT}...")
try:
    with serial.Serial(PORT, BAUDRATE, timeout=3) as ser:
        
        # --- EL CAMBIO CLAVE PARA USB NATIVO CDC ---
        ser.dtr = True
        ser.rts = True
        # -------------------------------------------
        
        print("Esperando 2 segundos (Estabilización USB CDC)...")
        time.sleep(2)
        ser.reset_input_buffer()
        
        print("\n--- Escuchando a la placa (Prueba TX ESP32) ---")
        for _ in range(2):
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"ESP32 dice: {line}")
            
        print("\n--- Enviando comando 0x01 (Prueba RX ESP32) ---")
        ser.write(b'\x01')
        ser.flush() 
        
        print("\n--- Esperando respuesta ---")
        for _ in range(4):
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"ESP32 responde: {line}")

except serial.SerialException as e:
    print(f"Error de puerto: {e}")