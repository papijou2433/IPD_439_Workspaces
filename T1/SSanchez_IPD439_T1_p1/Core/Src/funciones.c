/*
 * funciones.c
 *
 *  Created on: Mar 24, 2026
 *      Author: sebas
 */
#include "dma.h"
#include "gpio.h"
#include "funciones.h"
#include <string.h>






/*
Código sacado de la sig página https://wiki.st.com/stm32mcu/wiki/Getting_started_with_DMA
*/
void Transferir_dma_data(DMA_HandleTypeDef *hdma, uint32_t SrcAddress, uint32_t DstAddress, uint32_t DataLength,GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin)
{

    HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_RESET);
    HAL_DMA_Start(hdma, SrcAddress, DstAddress, DataLength);

    while(HAL_DMA_PollForTransfer(hdma, HAL_DMA_FULL_TRANSFER, 100) != HAL_OK)
    {

    }

    HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_SET);
}

void Transferir_cpy_data(uint32_t SrcAddress, uint32_t DstAddress,uint32_t DataLength,GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin){
	HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_RESET);
	memcpy(DstAddress,SrcAddress,DataLength);
	HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_SET);
}


