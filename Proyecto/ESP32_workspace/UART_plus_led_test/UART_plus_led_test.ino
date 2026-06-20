const int ledPin = 47; // GPIO47, cableado internamente al LED RGB

void setup() {
  Serial.begin(115200);

  // Dar tiempo crítico para que la PC enumere el dispositivo USB CDC
  delay(3000); 

  Serial.println("\n=========================================");
  Serial.println("   DIAGNÓSTICO DE UART CDC (TX/RX)       ");
  Serial.println("=========================================");
}

unsigned long lastTxTime = 0;
bool ledState = false;

void loop() {
  // 1. Diagnóstico de TX (ESP32 hacia el Host)
  if (millis() - lastTxTime > 2000) {
    Serial.println("[TX] ESP32 activo. Esperando señal de trigger (0x01)...");
    lastTxTime = millis();
    
    // Toggle del LED integrado (Rojo muy tenue para indicar vida)
    if (ledState) {
      neopixelWrite(ledPin, 10, 0, 0); 
    } else {
      neopixelWrite(ledPin, 0, 0, 0);
    }
    ledState = !ledState;
  }

  // 2. Diagnóstico de RX (Host hacia ESP32)
  if (Serial.available() > 0) {
    byte command = Serial.read();
    
    Serial.print("[RX] Byte recibido: 0x");
    if (command < 0x10) Serial.print("0");
    Serial.println(command, HEX);

    // Validación estricta del comando de inicio
    if (command == 0x01) {
      Serial.println(">>> COMANDO 0x01 ACEPTADO EXITOSAMENTE <<<");
      
      // Feedback visual inmediato: 3 destellos verdes rápidos
      for (int i = 0; i < 3; i++) {
        neopixelWrite(ledPin, 0, 50, 0);
        delay(100);
        neopixelWrite(ledPin, 0, 0, 0);
        delay(100);
      }
    }
  }
}