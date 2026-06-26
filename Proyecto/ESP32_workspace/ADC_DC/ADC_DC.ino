//#define NUM_SAMPLES 40000 
#define NUM_SAMPLES 16384
#define LED_BLINK_ms 500

const int adcPin = 1;
const int ledPin = 47;

volatile uint16_t adcBuffer[NUM_SAMPLES];
volatile float temp_buffer[2];
volatile int counter = 0;

volatile bool busy = false;
volatile bool done = false;
volatile bool ledState = false;
volatile bool cal = false;
volatile bool take_sample = false;

volatile unsigned long curr_Millis = 0;
volatile unsigned long prev_Millis = 0;

hw_timer_t * timer = NULL;

void IRAM_ATTR onTimer() {
  if (busy) {
    take_sample = true; 
  }
}
 
void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  timer = timerBegin(1000000);
  timerAttachInterrupt(timer, &onTimer);
  timerAlarm(timer, 100, true, 0); // Freq 10kHz
  //timerAlarm(timer, 20, true, 0); // Freq 50kHz
  
  timerStop(timer);
}

void loop() {
  if (!busy && !done) {
    curr_Millis = millis();
    if (curr_Millis - prev_Millis >= LED_BLINK_ms) {
      prev_Millis = curr_Millis;
      ledState = !ledState;
      if (ledState) neopixelWrite(ledPin, 0, 0, 10);
      else neopixelWrite(ledPin, 0, 0, 0);
    }
  }
  
  if (Serial.available() > 0) {
    byte command = Serial.read();

    if (!busy && !done) {
      counter = 0;
      take_sample = false;
      temp_buffer[0] = temperatureRead();
      neopixelWrite(ledPin, 0, 0, 0);
      
      switch (command) {
        case 0x01: analogSetAttenuation(ADC_11db); busy=true; cal=false; break;
        case 0x02: analogSetAttenuation(ADC_6db); busy=true; cal=false; break;
        case 0x03: analogSetAttenuation(ADC_2_5db); busy=true; cal=false; break;
        case 0x04: analogSetAttenuation(ADC_0db); busy=true; cal=false; break;
        case 0x05: analogSetAttenuation(ADC_11db); busy=true; cal=true; break;
        case 0x06: analogSetAttenuation(ADC_6db); busy=true; cal=true; break;
        case 0x07: analogSetAttenuation(ADC_2_5db); busy=true; cal=true; break;
        case 0x08: analogSetAttenuation(ADC_0db); busy=true; cal=true; break;
      }
      
      if(busy) {
        timerRestart(timer);
        timerStart(timer);
      }
    }
  }

  // Lectura segura fuera de la interrupción
  if (busy && take_sample) {
    take_sample = false;
    
    if (!cal) {
      adcBuffer[counter] = analogRead(adcPin);
    } else {
      adcBuffer[counter] = analogReadMilliVolts(adcPin);
    }
    
    counter++;
    
    if (counter >= NUM_SAMPLES) {
      busy = false;
      done = true;
      counter=0;
      timerStop(timer);
    }
  }

  if (done) {
    temp_buffer[1] = temperatureRead();
    
    Serial.println(temp_buffer[0]);
    Serial.println(temp_buffer[1]);
    
    for (int i = 0; i < NUM_SAMPLES; i++) {
      Serial.println(adcBuffer[i]);
    }

    done = false;
  }
}