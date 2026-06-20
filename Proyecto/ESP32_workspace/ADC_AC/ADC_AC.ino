#include "esp_adc/adc_continuous.h"

#define NUM_SAMPLES 16384
#define READ_LEN 1024
#define LED_BLINK_ms 500

const int adcPin = 1;
const int ledPin = 47;

volatile uint16_t adcBuffer[NUM_SAMPLES];
uint8_t dma_rx_buffer[READ_LEN];
//volatile float temp_buffer[2];
volatile int counter = 0;

volatile bool busy = false;
volatile bool done = false;
volatile bool ledState = false;

unsigned long curr_Millis = 0;
unsigned long prev_Millis = 0;

adc_continuous_handle_t dma_adc_handle = NULL;

void init_adc_dma(adc_channel_t channel, adc_atten_t attenuation) {
  if (dma_adc_handle != NULL) {
    adc_continuous_deinit(dma_adc_handle);
    dma_adc_handle = NULL;
  }
  
  adc_continuous_handle_cfg_t adc_config;
  adc_config.max_store_buf_size = 4096;
  adc_config.conv_frame_size = READ_LEN;
  adc_continuous_new_handle(&adc_config, &dma_adc_handle);

  adc_digi_pattern_config_t adc_pattern[1];
  adc_pattern[0].atten = attenuation;
  adc_pattern[0].channel = channel;
  adc_pattern[0].unit = ADC_UNIT_1; 
  adc_pattern[0].bit_width = SOC_ADC_DIGI_MAX_BITWIDTH;
  
  adc_continuous_config_t cont_cfg;
  cont_cfg.pattern_num = 1;
  cont_cfg.adc_pattern = adc_pattern;
  cont_cfg.sample_freq_hz = 100000;
  cont_cfg.conv_mode = ADC_CONV_SINGLE_UNIT_1;
  cont_cfg.format = ADC_DIGI_OUTPUT_FORMAT_TYPE2;
  adc_continuous_config(dma_adc_handle, &cont_cfg);
}

void capture_samples_dma() {
  adc_continuous_start(dma_adc_handle);
  
  uint32_t ret_num = 0;
  uint32_t samples_collected = 0;

  while (samples_collected < NUM_SAMPLES) {
    esp_err_t ret = adc_continuous_read(dma_adc_handle, dma_rx_buffer, READ_LEN, &ret_num, 100);
    
    if (ret == ESP_OK) {
      for (int i = 0; i < ret_num; i += 2) {
        if (samples_collected < NUM_SAMPLES) {
          adc_digi_output_data_t *p = (adc_digi_output_data_t*)&dma_rx_buffer[i];
          adcBuffer[samples_collected] = p->type2.data;
          samples_collected++;
        }
      }
    }
  }
  
  adc_continuous_stop(dma_adc_handle);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
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
      //temp_buffer[0] = temperatureRead();
      neopixelWrite(ledPin, 0, 0, 0);
      busy = true;
      
      switch (command) {
        case 0x01:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_11);
          capture_samples_dma();
          done = true;
          break;
        case 0x02:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_6);
          capture_samples_dma();
          done = true;
          break;
        case 0x03:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_2_5);
          capture_samples_dma();
          done = true;
          break;
        case 0x04:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_0);
          capture_samples_dma();
          done = true;
          break;
        case 0x05:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_11);
          capture_samples_dma();
          done = true;
          break;
        case 0x06:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_6);
          capture_samples_dma();
          done = true;
          break;
        case 0x07:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_2_5);
          capture_samples_dma();
          done = true;
          break;
        case 0x08:
          init_adc_dma(ADC_CHANNEL_0, ADC_ATTEN_DB_0);
          capture_samples_dma();
          done = true;
          break;
      }
      busy = false;
    }
  }

  if (done) {
    //temp_buffer[1] = temperatureRead();
    
    //Serial.println(temp_buffer[0]);
    //Serial.println(temp_buffer[1]);
    
    for (int i = 0; i < NUM_SAMPLES; i++) {
      Serial.println(adcBuffer[i]);
    }

    done = false;
  }
}