
const int adcPin = 6;

void setup() {
  Serial.begin(115200);
  delay(2000); 
  analogReadResolution(12);
  
  // atenuación a 11dB para rango de hasta app 3.1V
  analogSetPinAttenuation(adcPin, ADC_11db);
  
}

void loop() {
  int valorCrudo = analogRead(adcPin);
  float valor_decimal = ( valorCrudo/4095.0) * 3.3;
  int voltaje_mV = analogReadMilliVolts(adcPin);

  // Mostrar los resultados en el serial monitor
  Serial.print("Valor crudo decimal: ");
  Serial.print(valor_decimal);
  Serial.print("\t | \t");
  Serial.print("Voltaje calibrado: ");
  Serial.print(voltaje_mV);
  Serial.println(" mV");

  // Pausa de 100ms para no saturar el monitor
  delay(100);
}