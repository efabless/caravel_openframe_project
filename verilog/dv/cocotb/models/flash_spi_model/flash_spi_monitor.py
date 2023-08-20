import cocotb
from cocotb.triggers import RisingEdge, Edge
from collections import namedtuple

SPI_Transaction = namedtuple("SPI_Transaction", ["cs", "sdi", "sdo"])


class FlashSPI_Monitor():
    def __init__(self, dut_hdl, dbus_queue):
        self.spi_flash_hdl = dut_hdl.spiflash
        self._dbus_fork = cocotb.scheduler.add(self._flash_spi_monitor(dbus_queue))

    async def _flash_spi_monitor(self, queue):
        self._flash_spi_hdls()
        await cocotb.start(self.watch_cs(queue))
        while True:
            await RisingEdge(self.clk_hdl)
            transaction = SPI_Transaction(cs=self.cs_hdl.value, sdi=self.sdi_hdl.value, sdo=self.sdo_hdl.value)
            queue.put_nowait(transaction)
            cocotb.log.debug(f"[{__class__.__name__}][_spi_monitoring] sending transaction {transaction} to queue")
    
    async def watch_cs(self, queue):
        while True:
            await RisingEdge(self.cs_hdl)
            transaction = SPI_Transaction(cs=1, sdi=0, sdo=0)
            queue.put_nowait(transaction)
            cocotb.log.info(f"[{__class__.__name__}][_spi_monitoring] sending transaction {transaction} to queue")

    def _flash_spi_hdls(self):
        self.cs_hdl = self.spi_flash_hdl.csb
        self.clk_hdl = self.spi_flash_hdl.clk
        self.sdi_hdl = self.spi_flash_hdl.io0
        self.sdo_hdl = self.spi_flash_hdl.io1


