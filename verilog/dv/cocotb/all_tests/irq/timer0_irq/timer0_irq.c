#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
    if ((irqs & (1<<0xa)) != 0){ // condition for spi_master irq 
        set_debug_reg1(0xaC);
    }
    return regs;
}

void main(){
    timer0_irq_enable(1);
    timer0_oneshot_config(0,0x5F);
    while(1);
}