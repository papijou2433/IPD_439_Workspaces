/*
 * funciones.c
 *
 *  Created on: Mar 24, 2026
 *      Author: sebas
 */

#ifndef INC_FUNCIONES_C_
#define INC_FUNCIONES_C_



#endif /* INC_FUNCIONES_C_ */

#include "main.h"

void Transferir_dma_data(DMA_HandleTypeDef *hdma, uint32_t SrcAddress, uint32_t DstAddress, uint32_t DataLength,GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);
void Transferir_cpy_data(uint32_t SrcAddress, uint32_t DstAddress,uint32_t DataLength,GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);
