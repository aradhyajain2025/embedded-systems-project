#ifndef SENSORS_H
#define SENSORS_H
#include <stdint.h>
void sensors_init(void);
uint8_t sensor_read_pir(void);
uint8_t sensor_read_sound(void);
uint16_t sensor_read_distance_cm(void);
#endif