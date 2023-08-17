from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from openframe import OpenFrame


@cocotb.test()
@report_test
async def external2_irq(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=7264)
    openframe = OpenFrame(caravelEnv)
    await openframe.wait_reg1(0xAA)
    cocotb.log.info("[TEST] configuration finished")
    caravelEnv.drive_gpio_in(12, 1)
    cocotb.log.info("[TEST] trigger interrupt by assert the io 12")
    await openframe.wait_reg1(0x8C)
    cocotb.log.info("[TEST] received 0x8C at reg1 from interrupt handler")
