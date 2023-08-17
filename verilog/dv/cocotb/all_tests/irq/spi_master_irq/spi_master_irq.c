#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
    if ((irqs & (1<<9)) != 0){ // condition for spi_master irq 
        set_debug_reg1(0x9C);
    }
    return regs;
}

void main(){
    // configure spi ios 
    GPIO_Configure(8, GPIO_MODE_VECTOR_OUTPUT);
    GPIO_Configure(9, GPIO_MODE_VECTOR_OUTPUT);
    GPIO_Configure(10, GPIO_MODE_VECTOR_INPUT_PULLDOWN);
    GPIO_Configure(11, GPIO_MODE_VECTOR_OUTPUT);
    spi_irq_enable(1);
    set_debug_reg1(0xAA); // finish config

    // send dummy spi operation to test
    spi_stream(1);
    spi_enable(1);
    spi_write(0x02);
    spi_stream(0);
    spi_enable(0);

    while(1);
}