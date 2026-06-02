#include "tim.h"
#include "adc.h"
#include "gpio.h"
#include "usart.h"
#include "dma.h"
#include "main.h"

#define datos 16384
#define MAX_TEMP_SAMPLES 10

volatile int timer = 0;
volatile int send_data = 0;
volatile uint8_t rx_data;
extern uint16_t adc_buffer[datos];

volatile int temp_timer = 0;
volatile int send_temp_data = 0;
volatile uint16_t temp_adc_raw = 0;
volatile int temp_counter = 0;

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART2) {
        if (rx_data == 0x01 && timer == 0) {
            timer = 1;
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0, GPIO_PIN_SET);
            HAL_ADC_Start_DMA(&hadc2, (uint32_t *)adc_buffer, datos);
            HAL_TIM_Base_Start(&htim2);
        }
        else if (rx_data == 0x02) {
            if (temp_timer == 0) {
                temp_timer = 1;
                temp_counter = 0;
                HAL_TIM_Base_Start_IT(&htim3);
            }
        }
        HAL_UART_Receive_IT(&huart2, (uint8_t *)&rx_data, 1);
    }
}


void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC2) {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0, GPIO_PIN_RESET);
    }
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC2) {
        HAL_TIM_Base_Stop(&htim2);
        HAL_ADC_Stop_DMA(&hadc2);
        timer = 0;
        send_data = 1;
    }
    if (hadc->Instance == ADC1) {
        temp_adc_raw = HAL_ADC_GetValue(&hadc1);
        send_temp_data = 1;
    }
}
