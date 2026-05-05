#include "main.h"

void stats(uint16_t *data, float *media){
	uint32_t suma=0;
	int i=0;
	for(i=0;i<20000;i++){
		suma+=data[i];
	}
	*media = (float)suma/20000;
}
