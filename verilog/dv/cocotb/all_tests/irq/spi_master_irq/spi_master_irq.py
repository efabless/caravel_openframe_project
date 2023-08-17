from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from openframe import OpenFrame
from cocotb.triggers import FallingEdge, RisingEdge, Combine

spi_finish_time = 0

interrupt_trigger_time = 0

@cocotb.test()
@report_test
async def spi_master_irq(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=153546)
    openframe = OpenFrame(caravelEnv)
    await openframe.wait_reg1(0xAA)
    cocotb.log.info("[TEST] received 0xAA at reg1 configuration finished")
    spi_command_recieved = await cocotb.start(wait_for_spi_command_to_finish(dut))
    interrupt_triggered = await cocotb.start(wait_for_interrupt(openframe))
    # wait for both to finish
    await Combine(spi_command_recieved, interrupt_triggered)
    if spi_finish_time > interrupt_trigger_time:
        cocotb.log.error(f"[TEST] interrupt happened before receiving the spi command trigger at {interrupt_trigger_time} and spi command finish at {spi_finish_time}")
    else:
        cocotb.log.info(f"[TEST] interrupt happened after receiving the spi command trigger at {interrupt_trigger_time} and spi command finish at {spi_finish_time}")


async def wait_for_spi_command_to_finish(dut):
    cs_hdl = dut.gpio8_monitor
    clk_hdl = dut.gpio9_monitor
    # wait until the command send and finished
    await FallingEdge(cs_hdl)
    cocotb.log.info("[wait_for_spi_command_to_finish] start send spi command")
    # wait for reading 8 bits
    for _ in range(8):
        await RisingEdge(clk_hdl)
    cocotb.log.info("[wait_for_spi_command_to_finish] finish send spi command")
    global spi_finish_time
    spi_finish_time = cocotb.utils.get_sim_time("ns")


async def wait_for_interrupt(openframe):
    await openframe.wait_reg1(0x9C)
    cocotb.log.info("[wait_for_interrupt] trigger interrupt")
    global interrupt_trigger_time
    interrupt_trigger_time = cocotb.utils.get_sim_time("ns")
