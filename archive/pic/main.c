
#include <xc.h>
#include <stdint.h>
#include "frame.h"
#include "fake_sensors.h"
#include "sensors.h"

#pragma config FOSC = XT, WDTE = OFF, PWRTE = OFF, BOREN = OFF
#pragma config LVP = OFF, CPD = OFF, WRT = OFF, CP = OFF

#define _XTAL_FREQ 4000000
#define USE_FAKE_SENSORS 1  

char frame[20];
volatile unsigned char tick_ms = 0;
volatile unsigned char sample_due = 0;

void UART_Init(void)
{
    TRISC6 = 1;
    TRISC7 = 1;
    TXSTA = 0;
    RCSTA = 0;
    BRGH = 1;
    SPBRG = 25;
    SYNC = 0;
    SPEN = 1;
    TXEN = 1;
}

void UART_WriteChar(char c)
{
    while (!TXIF)
        ;
    TXREG = c;
}

void UART_WriteString(const char *text)
{
    while (*text)
        UART_WriteChar(*text++);
}

void Timer2_Init(void)
{
    PR2 = 249;
    T2CON = 0x05;
    TMR2IF = 0;
    TMR2IE = 1;
    PEIE = 1;
    GIE = 1;
}

void __interrupt() ISR(void)
{
    if (TMR2IF)
    {
        TMR2IF = 0;
        tick_ms++;

        if (tick_ms >= 200)
        {
            tick_ms = 0;
            sample_due = 1;
        }
    }
}

void main(void)
{
    uint8_t pir;
    uint16_t distance;
    uint8_t sound;

    UART_Init();
    Timer2_Init();
    sensors_init();

    while (1)
    {
        if (sample_due)
        {
            sample_due = 0;

#if USE_FAKE_SENSORS
            fake_sensors_next(&pir, &distance, &sound);
#else
            pir = sensor_read_pir();
            sound = sensor_read_sound();
            distance = sensor_read_distance_cm();
#endif

            frame_build(frame, pir, distance, sound);
            UART_WriteString(frame);
        }
    }
}