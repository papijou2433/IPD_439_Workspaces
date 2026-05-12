#include "main.h"
#include "gpio.h"
volatile uint8_t modo=0;

//GPIO_PIN_RESET = 0u
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin){
	if(GPIO_Pin==GPIO_PIN_13){
		modo=0;
			if(HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_0)!=GPIO_PIN_RESET){
				modo+=1;
			}if(HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_1)!=GPIO_PIN_RESET){
				modo+=2;
			}
			if(HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0)!=GPIO_PIN_RESET){
				modo+=4;
		}
	}
}
