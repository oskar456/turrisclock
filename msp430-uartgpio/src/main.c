/******************************************************************************
 * Software UART example for MSP430.
 *
 * Stefan Wendler
 * sw@kaltpost.de
 * http://gpio.kaltpost.de
 *
 * Echos back each character received enclosed in square brackets "[" and "]".
 * Use /dev/ttyACM0 at 9600 Bauds (and 8,N,1).
 ******************************************************************************/

#include <msp430.h>
#include <stdint.h>

#include "uart.h"

/**
 * Main routine
 */
int main(void)
{
     WDTCTL = WDTPW + WDTHOLD; 	// Stop WDT

     BCSCTL1 = CALBC1_1MHZ; 		// Set range
     DCOCTL = CALDCO_1MHZ; 		// SMCLK = DCO = 1MHz

     uart_init();

     __enable_interrupt();


     uint8_t c;

#define     LED0                  BIT0
#define     LED1                  BIT6
#define     LED_DIR               P1DIR
#define     LED_OUT               P1OUT
     LED_OUT = 0;
     LED_DIR |= LED0 | LED1;

     while(1) {
          if(uart_getc(&c)) {
               switch(c) {
		case '0':
			       LED_OUT &= ~(LED0|LED1);
			       break;
		case '1':
			       LED_OUT &= ~LED1;
			       LED_OUT |= LED0;
			       break;
		case '2':
			       LED_OUT &= ~LED0;
			       LED_OUT |= LED1;
			       break;
		case '3':
			       LED_OUT |= (LED0|LED1);
			       break;
               }
          }
     }
}

