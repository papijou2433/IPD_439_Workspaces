#include "main.h"

void stats(uint16_t *data, float *media){
	uint32_t suma=0;
	int i=0;
	for(i=0;i<16354;i++){
		suma+=data[i];
	}
	*media = (float)suma/16354;
}
