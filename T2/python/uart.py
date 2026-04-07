import serial
import random

com = serial.Serial(port='COM5',baudrate=115200,timeout=5)

mode = 0
num = []

if(mode==1):
    # Modo no aleatorio para pruebas
    i=0
    while(i<100):
        num.append(i)
        i=i+1     
else:
    # Modo aleatorio 
    i=0
    while(i<100):
        num.append(random.randint(-1500,1500))
        i=i+1
for dato in num:
    tx_msg = str(dato) + '\n'
    com.write(tx_msg.encode('utf-8'))

respuesta_media = com.readline().decode('utf-8').strip()
        
respuesta_desv = com.readline().decode('utf-8').strip()

promedio_real = sum(num)/100.00
var_real=0
for x in num:
    var_real += (x-promedio_real)**2
var_real = var_real/100.00
desv_real = var_real**0.5
print("Promedio por python:",promedio_real,"\n")
print("Promedio por STM32:",respuesta_media,"\n")
print("Desviacion por python:",desv_real,"\n")
print("Desviacion por STM32:",respuesta_desv,"\n")