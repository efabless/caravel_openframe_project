#include <openframe.h>


uint32_t *irq(uint32_t *regs, uint32_t irqs){
    if ((irqs & (1<<0xb)) != 0){ // condition for timer1 irq 
        set_debug_reg1(0xbC);
    }
    return regs;
}

void main(){
    timer1_irq_enable(1);
    timer1_oneshot_config(0,0x5F);
    while(1);
}