#include <xc.h>
#include "sensors.h"

#define _XTAL_FREQ 4000000

void sensors_init(void)
{
    TRISB0 = 1;     /* RB0 = PIR output */
    TRISB1 = 1;     /* RB1 = sound sensor digital output */
    TRISB2 = 0;     /* RB2 = HC-SR04 trigger (output) */
    TRISB3 = 1;     /* RB3 = HC-SR04 echo (input) */
    RB2 = 0;
    T1CON = 0x00;   /* Timer1 off, 1:1 prescaler, internal clock: 1 count = 1 us */
}

uint8_t sensor_read_pir(void)
{
    return RB0 ? 1 : 0;
}

uint8_t sensor_read_sound(void)
{
    return RB1 ? 1 : 0;
}

uint16_t sensor_read_distance_cm(void)
{
    uint16_t start;
    uint16_t elapsed;

    RB2 = 1;
    __delay_us(10);
    RB2 = 0;

    T1CON = 0x00;
    TMR1H = 0;
    TMR1L = 0;
    T1CON = 0x01;

    while (!RB3)
    {
        if (TMR1H >= 0x75)
        {
            T1CON = 0x00;
            return 0;
        }
    }

    start = ((uint16_t)TMR1H << 8) | TMR1L;

    while (RB3)
    {
        elapsed = (uint16_t)((((uint16_t)TMR1H << 8) | TMR1L) - start);

        if (elapsed >= 23200)
        {
            T1CON = 0x00;
            return 0;
        }
    }

    T1CON = 0x00;
    elapsed = (uint16_t)((((uint16_t)TMR1H << 8) | TMR1L) - start);

    return (elapsed >= 116 && elapsed <= 23200) ? elapsed / 58 : 0;
}