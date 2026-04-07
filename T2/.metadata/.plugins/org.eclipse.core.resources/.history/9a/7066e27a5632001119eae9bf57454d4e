/*
 * interrupciones.c
 *
 *  Created on: Apr 6, 2026
 *      Author: sebas
 */
/// Put a Message into a Queue or timeout if Queue is full.
/// \param[in]     mq_id         message queue ID obtained by \ref osMessageQueueNew.
/// \param[in]     msg_ptr       pointer to buffer with message to put into a queue.
/// \param[in]     msg_prio      message priority.
/// \param[in]     timeout       \ref CMSIS_RTOS_TimeOutValue or 0 in case of no time-out.
/// \return status code that indicates the execution status of the function.
// osStatus_t osMessageQueuePut (osMessageQueueId_t mq_id, const void *msg_ptr, uint8_t msg_prio, uint32_t timeout);
#include "main.h"
#include "cmsis_os.h"
#include "usart.h"
#include "FreeRTOS.h"
#include <stdlib.h>
extern volatile uint8_t rx_byte;
volatile uint8_t rx_i=0;
// se limitó el número aleatorio a los rangos de -1500 a 1500, por lo que solo se necesita
// un máximo de 6  bytes (contando el \n para indicar término del string)
char rx_buffer[6]; //
int valor=0;
extern osMessageQueueId_t FIFO_QueueHandle;
//osEventFlagsNew
void HAL_UART_RxCpltCallback (UART_HandleTypeDef *huart){
	if(huart->Instance==USART2){
			if(rx_byte=='\n'||rx_byte=='\0'||rx_byte=='\r'){
				// se envía el byte de termino de envío de datos o del string
				rx_buffer[rx_i]='\0';
				valor = atoi(rx_buffer);
				osMessageQueuePut(FIFO_QueueHandle,&valor,0,0);
				rx_i=0;
			}
			else{
				if(rx_i<5){
					rx_buffer[rx_i]=rx_byte;
					rx_i++;
				}
			}
	HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
	}
}
