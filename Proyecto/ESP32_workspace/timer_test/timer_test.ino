const uint8_t Pin=2;
hw_timer_t *My_timer=NULL;
volatile bool check_temp=false;
volatile bool pinState=false;
void IRAM_ATTR onTimer(){
  check_temp=true; 
  pinState=!pinState;
  digitalWrite(Pin,pinState);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(Pin,OUTPUT);
  digitalWrite(Pin,LOW);
  My_timer = timerBegin(1000000);
  timerAttachInterrupt(My_timer, &onTimer);
  timerAlarm(My_timer, 1000000, true, 0);
  timerRestart(My_timer);
}

void loop() {
  if(check_temp){
    check_temp=false;
    float tempC = temperatureRead();
    Serial.print("Temperatura del chip: ");
    Serial.print(tempC);
    Serial.println(" °C");
  }

}
