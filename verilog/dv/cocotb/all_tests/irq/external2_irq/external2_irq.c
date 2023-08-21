#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
    if ((irqs & (1<<8)) != 0){ // condition for external2 irq 
        set_debug_reg1(0x8C);
    }
    return regs;
}

void main(){
    // configure io 7 as input pulldown
    GPIO_Configure(12, GPIO_MODE_VECTOR_INPUT_PULLDOWN);
    set_debug_reg1(0xAA);
    while(1);
}