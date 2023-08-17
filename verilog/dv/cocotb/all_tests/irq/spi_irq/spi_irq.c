#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
    if ((irqs & (1<<6)) != 0){ // condition for spi irq 
        set_debug_reg1(0x7C);
    }
    return regs;
}

void main(){
    set_debug_reg1(0xAA);
    while(1);
}