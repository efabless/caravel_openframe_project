
from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from cocotb.triggers import First, Edge, ClockCycles
from openframe import OpenFrame
@cocotb.test()
@report_test
async def temp(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=11188117)
    caravelEnv.drive_gpio_in((38, 0), 0)  # drive all gpios with 0 to made pan_gpio_in =0 rather than x
    openframe = OpenFrame(caravelEnv)
    await openframe.wait_any_change_reg1()
    await ClockCycles(caravelEnv.clk, 1)
    expected = openframe.read_debug_reg1() & 0xFFFF
    recieved = openframe.read_debug_reg1() >> 16
    cocotb.log.info(f"[TEST] expected {hex(expected)} recieved {hex(recieved)}")

