#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
        set_debug_reg1(0x6C);
    if ((irqs & (1<<6)) != 0){ // condition for spi irq 
        set_debug_reg1(0x6C);
    }
    return regs;
}

void main(){
    set_debug_reg1(0xAA);
    for (int i = 0; i < 100; i++){
        set_debug_reg2(i);
    }
}