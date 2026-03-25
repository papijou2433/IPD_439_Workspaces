/*
 * callbacks.c
 *
 *  Created on: Mar 24, 2026
 *      Author: sebas
 */

#include "adc.h"
#include "dma.h"
#include "usart.h"
#include "gpio.h"
#include "tim.h"
#include "main.h"
#include <string.h>

volatile int timer = 0;
volatile int counter = 0;
volatile int send_data = 0;
char modes[2][4]={"DMA","CPU"};
extern uint16_t adc_buffer[200];
extern char mode[4];

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin){
	if(GPIO_Pin==BPB_Pin){
		if(timer==0){
			timer=1;
			counter=0;
			HAL_TIM_Base_Start_IT(&htim2);
		}
		else{

		}
	}
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim){
	if(htim->Instance==TIM2){
		if(counter<200){
			HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_RESET);
			// CPU == CPU
			if(strcmp(modes[1],mode)==0){
				HAL_ADC_Start_IT(&hadc1);
			}
			else{
				HAL_ADC_Start_DMA(&hadc1, (uint32_t *)&adc_buffer[counter],1);
				HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_SET);
				counter++;
			}
		}
		else{
			timer=0;
			send_data = 1;
			HAL_TIM_Base_Stop(&htim2);
		}
	}

}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc){
	if(hadc->Instance==ADC1){
		// CPU == CPU
		if(strcmp(modes[1],mode)==0){
			adc_buffer[counter] = HAL_ADC_GetValue(&hadc1);
			HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_SET);
			counter++;
		}

	}
}






