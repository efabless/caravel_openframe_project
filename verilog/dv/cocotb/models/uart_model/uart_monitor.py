import cocotb
from cocotb.triggers import Edge, FallingEdge, ClockCycles, NextTimeStep
from collections import namedtuple

UART_Transaction = namedtuple("UART_Transaction", ["type", "char", "clock_div"])


class UART_Monitor():
    def __init__(self, Caravel_env, uart_queue):
        self.clk = Caravel_env.clk
        self.uart_hdl = Caravel_env.dut.uut.user_project.openframe_example.simpleuart.simpleuart
        self._uart_fork = cocotb.scheduler.add(self._uart_monitor(uart_queue))

    async def _uart_monitor(self, queue):
        self._uart_hdls()
        while True:
            if self.uart_en_hdl.value.integer == 0:
                await Edge(self.uart_en_hdl)  # wait until uart is enabled
            rx_fork = await cocotb.start(self._uart_rx_monitor(queue))
            tx_fork = await cocotb.start(self._uart_tx_monitor(queue))
            await Edge(self.uart_en_hdl)  # wait until uart is disabled
            rx_fork.kill()
            tx_fork.kill()

    async def _uart_rx_monitor(self, queue,  not_ascii=False):
        while True:
            char = ""
            await FallingEdge(self.wb_uart_rx_hdl)  # start of char
            bit_cycles = self.uart_divider_hdl.value.integer + 2
            await ClockCycles(self.clk, bit_cycles)
            await ClockCycles(self.clk, int(bit_cycles/2))
            await NextTimeStep()
            for i in range(8):
                char = self.wb_uart_rx_hdl.value.binstr + char
                await ClockCycles(self.clk, bit_cycles)
                await NextTimeStep()
            transaction = UART_Transaction(
                type="rx", char=chr(int(char, 2)) if not not_ascii else hex(int(char, 2)),clock_div=bit_cycles-2)
            queue.put_nowait(transaction)
            cocotb.log.debug(f"[{__class__.__name__}][_uart_rx_monitor] sending transaction {transaction} to queue")

    async def _uart_tx_monitor(self, queue, not_ascii=False):
        while True:
            char = ""
            await FallingEdge(self.wb_uart_tx_hdl)
            bit_cycles = self.uart_divider_hdl.value.integer + 2
            await ClockCycles(self.clk, bit_cycles)
            await ClockCycles(self.clk, int(bit_cycles/2))
            for i in range(8):
                char = self.wb_uart_tx_hdl.value.binstr + char
                await ClockCycles(self.clk, bit_cycles)
            transaction = UART_Transaction(
                type="tx", char=chr(int(char, 2)) if not not_ascii else hex(int(char, 2)), clock_div=bit_cycles-2)
            queue.put_nowait(transaction)
            cocotb.log.debug(f"[{__class__.__name__}][_uart_tx_monitor] sending transaction {transaction} to queue")

    def _uart_hdls(self):
        self.uart_en_hdl = self.uart_hdl.enabled
        self.uart_divider_hdl = self.uart_hdl.cfg_divider
        self.wb_uart_rx_hdl = self.uart_hdl.ser_rx
        self.wb_uart_tx_hdl = self.uart_hdl.ser_tx
