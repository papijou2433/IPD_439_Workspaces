import serial
import random
def init_bootloader(puerto):
    # puerto = 'COM5'
    com = serial.Serial(port=puerto,baudrate=115200,parity=serial.PARITY_EVEN,timeout=1,stopbits=1.0)
    init=b'\x7f'
    ack=b'\x79'
    nack=b'\x1f'
    # eliminar basura previa just in cases
    com.reset_input_buffer()
    com.write(init)
    respuesta=com.read(1)
    if(respuesta==ack):
        print("Inicializado correctamente\n")
        com.close()
        return 0
    elif(respuesta==nack) :
        print("No se logró inicializar o ya está inicializado (NACK)\n")
        com.close()
        return 1
    else:
        print("Error inesperado o timeout\n")
        com.close()
        return 2
import serial

def read_mem(start_address, length_to_read, puerto):
    # puerto = 'COM5'
    # start_address = b'\x08\x00\x00\x00' (4 bytes)
    # length_to_read = b'\xff'
    # no había usado el formato b'\x' antes y como que me terminó gustando ajja
    n_minus_1 = length_to_read[0]
    bytes_esperados = n_minus_1 + 1 

    try:
        com = serial.Serial(port=puerto, baudrate=115200, parity=serial.PARITY_EVEN, timeout=1.0, stopbits=1.0)
        cmd_read = b'\x11\xEE'
        ack = b'\x79'
        nack = b'\x1F'
        com.reset_input_buffer()
        com.write(cmd_read)
        # revisar si ta bien
        if com.read(1) != ack:
            print("Error: El bootloader rechazó el comando Read (0x11).")
            com.close()
            return None
        print(f"Iniciando lectura en la dirección 0x{start_address.hex().upper()}...\n")
        addr_checksum = start_address[0] ^ start_address[1] ^ start_address[2] ^ start_address[3]
        com.write(start_address + bytes([addr_checksum]))
        
        if com.read(1) != ack:
            print("Error: El bootloader rechazó la dirección de memoria (Checksum incorrecto o dirección protegida).")
            com.close()
            return None
            
        len_checksum = n_minus_1 ^ 0xFF
        com.write(length_to_read + bytes([len_checksum]))
        
        if com.read(1) != ack:
            print("Error: El bootloader rechazó la longitud.")
            com.close()
            return None
        
        datos = com.read(bytes_esperados)
        com.close()
        
        if len(datos) == bytes_esperados:
            print(f"¡Éxito! Se leyeron {len(datos)} bytes correctamente.\n")
            return datos
        else:
            print(f"Advertencia: Se esperaban {bytes_esperados} bytes pero se recibieron {len(datos)}.\n")
            return datos
            
    except serial.SerialException as e:
        print(f"Error de comunicación en el puerto {puerto}: {e}\n")
        return None


datos=[[]]
inicializado=input("Se inicializó el bootloader previamente? (y/n)\n")
puerto_actual = 'COM5'
direccion_base = b'\x08\x00\x00\x00'
longitud_lectura = b'\xff'         
if inicializado.strip().lower() == 'n':
    print(f"Intentando inicializar el bootloader en {puerto_actual}...")
    estado_init = init_bootloader(puerto_actual)
    if estado_init == 2:
        print("Abortando script por fallo crítico de comunicación.")

print("\nProcediendo con la lectura de memoria...")
datos_obtenidos = read_mem(direccion_base, longitud_lectura, puerto_actual)

if datos_obtenidos:
    print("-" * 60)
    print("DUMP DE MEMORIA (Formato Hexadecimal)")
    print("-" * 60)
    
    for i in range(0, len(datos_obtenidos), 16):
        bloque = datos_obtenidos[i:i+16]
        hex_str = " ".join([f"{b:02X}" for b in bloque])
        offset = i
        print(f"Offset 0x{offset:04X} | {hex_str}")
        
    print("-" * 60)
else:
    print("No se pudieron recuperar los datos de la memoria.")