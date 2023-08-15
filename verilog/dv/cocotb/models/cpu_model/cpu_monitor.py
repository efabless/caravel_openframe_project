import cocotb
from cocotb.triggers import RisingEdge
from collections import namedtuple

WB_Transaction = namedtuple("WB_Transaction", ["address", "write", "data", "select"])


class CPU_Monitor():
    def __init__(self, openframe_example_hdl, dbus_queue):
        self.cpu_hdl = openframe_example_hdl.cpu
        self._dbus_fork = cocotb.scheduler.add(self._dbus_monitor(dbus_queue))

    async def _dbus_monitor(self, queue):
        self._dbus_hdls()
        while True:
            # valid transaction only happened if ack is sent
            await RisingEdge(self.dbus_ack_hdl)
            is_write = self.dbus_we_hdl.value.integer
            transaction = WB_Transaction(address=self.dbus_adr_hdl.value.integer, write=is_write, data=self.dbus_data_write_hdl.value if is_write else self.dbus_data_read_hdl.value, select=self.dbus_sel_hdl.value.integer)
            queue.put_nowait(transaction)
            cocotb.log.debug(f"[{__class__.__name__}][_dbus_monitor] sending transaction {transaction} to queue")

    def _dbus_hdls(self):
        self.dbus_clk_hdl = self.cpu_hdl.wb_clk_i
        self.dbus_rst_hdl = self.cpu_hdl.wb_rst_i
        self.dbus_adr_hdl = self.cpu_hdl.wbm_adr_o
        self.dbus_data_read_hdl = self.cpu_hdl.wbm_dat_i
        self.dbus_sel_hdl = self.cpu_hdl.wbm_sel_o
        self.dbus_we_hdl = self.cpu_hdl.wbm_we_o
        self.dbus_cyc_hdl = self.cpu_hdl.wbm_cyc_o
        self.dbus_stb_hdl = self.cpu_hdl.wbm_stb_o
        self.dbus_ack_hdl = self.cpu_hdl.wbm_ack_i
        self.dbus_data_write_hdl = self.cpu_hdl.wbm_dat_o


