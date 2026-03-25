/*
 * callbacks.h
 *
 *  Created on: Mar 24, 2026
 *      Author: sebas
 */

#ifndef INC_CALLBACKS_H_
#define INC_CALLBACKS_H_



#endif /* INC_CALLBACKS_H_ */
#include "main.h"

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin);
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc);
