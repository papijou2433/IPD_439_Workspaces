/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "funciones.h"
#include <string.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
const char data1[32]="este es un texto que contiene 3";
const char data2[64]="este es un texto que contiene 32este es un texto que contiene 3";
const char data4[128]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
const char data8[256]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
const char data16[512]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
const char data32[1024]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

char modes[2][4]={"dma","cpy"};
char orig[2][4]={"ram","fla"};
// ACA HAGO SET UP DE LA MEDICION QUE QUIERO REALIZAR
char mode[4]="cpy";
char origen[4]="fla";

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  /* USER CODE BEGIN 2 */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_1, GPIO_PIN_SET);
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0, GPIO_PIN_SET);


  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
  /* MEMORY
{
  RAM    (xrw)    : ORIGIN = 0x20000000,   LENGTH = 96K
  RAM2    (xrw)    : ORIGIN = 0x10000000,   LENGTH = 32K
  FLASH    (rx)    : ORIGIN = 0x8000000,   LENGTH = 1024K
}
revisar si const guarda en 0x8 en adelante
revisar si variables normales guardan en en 0x2 o 0x1
*/

   char data_1[32]="este es un texto que contiene 3";
   char data_2[64]="este es un texto que contiene 32este es un texto que contiene 3";
   char data_4[128]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
   char data_8[256]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
   char data_16[512]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";
   char data_32[1024]="este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 32este es un texto que contiene 3";

   char data_1_dst[32];
   char data_2_dst[64];
   char data_4_dst[128];
   char data_8_dst[256];
   char data_16_dst[512];
   char data_32_dst[1024];

   uint32_t dir_1;
   uint32_t dir_2;
   uint32_t dir_4;
   uint32_t dir_8;
   uint32_t dir_16;
   uint32_t dir_32;
   if(strcmp(orig[0],origen)==0){
	   dir_1 = (uint32_t) data_1;
	   dir_2 = (uint32_t) data_2;
	   dir_4 = (uint32_t) data_4;
	   dir_8 = (uint32_t) data_8;
	   dir_16= (uint32_t) data_16;
	   dir_32= (uint32_t) data_32;
   }
   else{
	   dir_1 = (uint32_t) data1;
	   dir_2 = (uint32_t) data2;
	   dir_4 = (uint32_t) data4;
	   dir_8 = (uint32_t) data8;
	   dir_16= (uint32_t) data16;
	   dir_32= (uint32_t) data32;
   }

// DMA_HandleTypeDef hdma_memtomem_dma1_channel1;
	/*
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_15, GPIO_PIN_RESET);
	    HAL_DMA_Start(&hdma_memtomem_dma1_channel1, data_1, data_1_dst, 32);

	    while(HAL_DMA_PollForTransfer(&hdma_memtomem_dma1_channel1, HAL_DMA_FULL_TRANSFER, 100) != HAL_OK)
	    {
	        __NOP();
	    }

	    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_15, GPIO_PIN_SET);*/

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	  if(strcmp(modes[0],mode)==0){
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_1 , (uint32_t) data_1_dst ,32,GPIOA,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_2 , (uint32_t) data_2_dst ,64,GPIOA,GPIO_PIN_1);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_4 , (uint32_t) data_4_dst ,128,GPIOA,GPIO_PIN_4);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_8 , (uint32_t) data_8_dst ,256,GPIOB,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_16 , (uint32_t) data_16_dst ,512,GPIOC,GPIO_PIN_1);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  Transferir_dma_data(&hdma_memtomem_dma1_channel1, dir_32 , (uint32_t) data_32_dst ,1024,GPIOC,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
		  //sorry profe por lo feo de la linea de verificación de error, pero preferí código horizontal antes
		  //que seguir haciendo lineas hacia abajo ajjajaj
	  }
	  else{
		  Transferir_cpy_data(dir_1 , (uint32_t) data_1_dst ,32,GPIOA,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
  		  Transferir_cpy_data(dir_2 , (uint32_t) data_2_dst ,64,GPIOA,GPIO_PIN_1);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
  		  Transferir_cpy_data(dir_4 , (uint32_t) data_4_dst ,128,GPIOA,GPIO_PIN_4);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
  		  Transferir_cpy_data(dir_8 , (uint32_t) data_8_dst ,256,GPIOB,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
  		  Transferir_cpy_data(dir_16 , (uint32_t) data_16_dst ,512,GPIOC,GPIO_PIN_1);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
  		  Transferir_cpy_data(dir_32 , (uint32_t) data_32_dst ,1024,GPIOC,GPIO_PIN_0);
		  if(strcmp((char *)dir_1,data_1_dst)!=0){HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);while(1);};
	  }

  }
  /* USER CODE END 3 */
}
/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 10;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
