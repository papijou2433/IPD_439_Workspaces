#define NUM_SAMPLES 1000 

const int adcPin = 1;     // GPIO1 -> ADC1_CH0
const int triggerPin = 2; // GPIO2 para el trigger del AD 2

volatile uint16_t adcBuffer[NUM_SAMPLES];
volatile int sampleIndex = 0;
volatile bool isSampling = false;
volatile bool samplingDone = false;

hw_timer_t * timer = NULL;

void IRAM_ATTR onTimer() {
  if (isSampling) {
    adcBuffer[sampleIndex] = analogRead(adcPin);
    sampleIndex++;
    
    if (sampleIndex >= NUM_SAMPLES) {
      isSampling = false;
      samplingDone = true;
      timerStop(timer); // Detener el temporizador para no muestrear mas
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);
  analogReadResolution(12);
  timer = timerBegin(1000000); // timer base a 1MHz 
  timerAttachInterrupt(timer, &onTimer);
  timerAlarm(timer, 250, true, 0); //counter de 250 para freq = 4kHz
  
  // detener timer para activar post recepción uart
  timerStop(timer);
}

void loop() {
  if (Serial.available() > 0) {
    byte command = Serial.read();

    if (command == 0x01 && !isSampling && !samplingDone) {
      sampleIndex = 0;
      
      // Levantar señal lógica (Trigger WaveForms)
      digitalWrite(triggerPin, HIGH);
      
      // Iniciar el muestreo exacto a 4 kHz
      isSampling = true;
      timerRestart(timer); // Reinicia la cuenta desde cero y arranca el timer
    }
  }

  if (samplingDone) {
    digitalWrite(triggerPin, LOW);

    // Enviar las 1000 mediciones
    for (int i = 0; i < NUM_SAMPLES; i++) {
      Serial.println(adcBuffer[i]);
    }

    samplingDone = false;
  }
}