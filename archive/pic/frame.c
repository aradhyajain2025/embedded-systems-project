#include "frame.h"

static const char HEX[] = "0123456789ABCDEF";

uint8_t frame_checksum(const char *s)
{
    uint8_t cs = 0;

    while (*s)
        cs ^= (uint8_t)*s++;

    return cs;
}

uint8_t frame_build(char *buf, uint8_t p, uint16_t d, uint8_t s)
{
    char *w = buf;
    uint8_t cs;

    if (d > 400)
        d = 0;

    if (d == 1)
        d = 2;

    *w++ = 'P';
    *w++ = ':';
    *w++ = p ? '1' : '0';
    *w++ = ',';
    *w++ = 'D';
    *w++ = ':';

    if (d >= 100)
        *w++ = (char)('0' + (d / 100));

    if (d >= 10)
        *w++ = (char)('0' + ((d / 10) % 10));

    *w++ = (char)('0' + (d % 10));

    *w++ = ',';
    *w++ = 'S';
    *w++ = ':';
    *w++ = s ? '1' : '0';
    *w = '\0';

    cs = frame_checksum(buf);

    *w++ = '*';
    *w++ = HEX[cs >> 4];
    *w++ = HEX[cs & 0x0F];
    *w++ = '\n';
    *w = '\0';

    return (uint8_t)(w - buf);
}