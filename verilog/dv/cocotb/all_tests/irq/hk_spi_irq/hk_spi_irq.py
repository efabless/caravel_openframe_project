from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from openframe import OpenFrame
from openframe import OpenFrameSPI


@cocotb.test()
@report_test
async def hk_spi_irq(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=7264)
    openframe = OpenFrame(caravelEnv)
    spi_master = OpenFrameSPI(caravelEnv)
    await openframe.wait_reg1(0xAA)
    cocotb.log.info("[TEST] received 0xAA at reg1")
    await spi_master.write_reg_spi(0xa, 1)
    cocotb.log.info("[TEST] trigger interrupt")
    await openframe.wait_reg1(0x6C)
    cocotb.log.info("[TEST] received 0x6C at reg1 from interrupt handler")
