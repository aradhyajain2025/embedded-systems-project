
#ifndef FRAME_H
#define FRAME_H

#include <stdint.h>

uint8_t frame_checksum(const char *s);
uint8_t frame_build(char *buf, uint8_t p, uint16_t d, uint8_t s);

#endif
