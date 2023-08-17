from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from openframe import OpenFrame


@cocotb.test()
@report_test
async def external1_irq(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=7320)
    openframe = OpenFrame(caravelEnv)
    await openframe.wait_reg1(0xAA)
    cocotb.log.info("[TEST] configuration finished")
    caravelEnv.drive_gpio_in(7, 1)
    cocotb.log.info("[TEST] trigger interrupt by assert the io 7")
    await openframe.wait_reg1(0x7C)
    cocotb.log.info("[TEST] received 0x7C at reg1 from interrupt handler")
