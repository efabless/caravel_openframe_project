from cocotb_coverage.coverage import CoverPoint, CoverCross
from collections import namedtuple
import cocotb

class UART_Coverage():
    def __init__(self) -> None:
        # initialize coverage no covearge happened just sample nothing so the coverge is initialized
        self.uart_cov(None, do_sampling=False)

    def uart_cov(self, operation, do_sampling=True):
        @CoverPoint(
            "top.openframe.uart.type",
            xf=lambda operation: operation.type,
            bins=["rx", "tx"]
        )
        @CoverPoint(
            "top.openframe.uart.char",
            xf=lambda operation: ord(operation.char),
            bins=[(0x0, 0x10), (0x10, 0x20), (0x20, 0x30), (0x30, 0x40), (0x40, 0x50), (0x50, 0x60), (0x60, 0x70), (0x70, 0x80)],
            bins_labels=["0 to 0x10", "0x10 to 0x20", "0x20 to 0x30", "0x30 to 0x40", "0x40 to 0x50", "0x50 to 0x60", "0x60 to 0x70", "0x70 to 0x80"],
            rel=lambda val, b: b[0] <= val <= b[1]
        )
        @CoverPoint(
            "top.openframe.uart.clk_divider",
            xf=lambda operation: operation.clock_div,
            bins=[(0x0, 0x5), (0x6, 0x1E)],
            bins_labels=["0 to 5", "6 to 30"],
            rel=lambda val, b: b[0] <= val <= b[1]
        )
        def sample(operation):
            pass
        if do_sampling:
            sample(operation)
