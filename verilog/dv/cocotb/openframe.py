import cocotb
from cocotb.triggers import Edge, First
from caravel_cocotb.caravel_interfaces import UART
from caravel_cocotb.caravel_interfaces import SPI
from models.cpu_model.cpu_model import CPU_Model
from models.flash_spi_model.flash_spi_model import FlashSPI_Model
from models.uart_model.uart_model import UART_Model

class OpenFrame:
    def __init__(self, caravelEnv):
        self.caravelEnv = caravelEnv
        openframe_example_hdl = caravelEnv.dut.uut.user_project.openframe_example
        if "GL" not in cocotb.plusargs:
            debug_hdl = openframe_example_hdl.debug_regs
            self.debug_reg1_hdl = debug_hdl.debug_reg_1
            self.debug_reg2_hdl = debug_hdl.debug_reg_2
        else:
            self.debug_reg1_hdl = [openframe_example_hdl._id(f"\debug_regs.debug_reg_1[{i}] ", False) for i in range(32)]
            self.debug_reg2_hdl = [openframe_example_hdl._id(f"\debug_regs.debug_reg_2[{i}] ", False) for i in range(32)]
        if "GL" not in cocotb.plusargs:
            self.cpu = CPU_Model(openframe_example_hdl)
            self.uart = UART_Model(self.caravelEnv)
            cocotb.plusargs["COVERAGE_COLLECT"] = True

        # FlashSPI_Model(caravelEnv.dut)

    async def wait_reg1(self, data):
        while True:
            if "GL" not in cocotb.plusargs:
                await Edge(self.debug_reg1_hdl)
            else:
                await First(*[Edge(self.debug_reg1_hdl[i]) for i in range(32)])
            if self.read_debug_reg1() == data:
                return
            else: 
                cocotb.log.info(f"[wait_reg1]: reg1 has data {self.read_debug_reg1()} instead of {hex(data)}")
            
    async def wait_any_change_reg1(self):
        while True:
            if "GL" not in cocotb.plusargs:
                await Edge(self.debug_reg1_hdl)
            else:
                await First(*[Edge(self.debug_reg1_hdl[i]) for i in range(32)])
            return
        
    async def wait_reg2(self, data):
        while True:
            if "GL" not in cocotb.plusargs:
                await Edge(self.debug_reg2_hdl)
            else:
                await First(*[Edge(self.debug_reg2_hdl[i]) for i in range(32)])
            if self.read_debug_reg2() == data:
                return
    
    async def wait_any_change_reg2(self):
        while True:
            if "GL" not in cocotb.plusargs:
                await Edge(self.debug_reg2_hdl)
            else:
                await First(*[Edge(self.debug_reg2_hdl[i]) for i in range(32)])
            return

    def read_debug_reg1(self):
        if "GL" not in cocotb.plusargs:
            return self.debug_reg1_hdl.value.integer
        else:
            try:
                return int("".join([self.debug_reg1_hdl[i].value.binstr for i in range(32)][::-1]), 2)
            except:
                return "".join([self.debug_reg1_hdl[i].value.binstr for i in range(32)][::-1])

    def read_debug_reg2(self):
        if "GL" not in cocotb.plusargs:
            return self.debug_reg2_hdl.value.integer
        else:
            return int("".join([self.debug_reg2_hdl[i].value.binstr for i in range(32)][::-1]), 2)

    def read_debug_reg1_str(self):
        if "GL" not in cocotb.plusargs:
            return self.debug_reg1_hdl.value.binstr
        else:
            return "".join([self.debug_reg1_hdl[i].value.binstr for i in range(32)])

    def read_debug_reg2_str(self):
        if "GL" not in cocotb.plusargs:
            return self.debug_reg2_hdl.value.binstr
        else:
            return "".join([self.debug_reg2_hdl[i].value.binstr for i in range(32)])

    # writing debug registers using backdoor because in GL
    # cpu can't be disabled for now because of different netlist names
    def write_debug_reg1_backdoor(self, data):
        self.debug_reg1_hdl.value = data

    def write_debug_reg2_backdoor(self, data):
        self.debug_reg2_hdl.value = data


class OpenFrameUART(UART):
    def __init__(self, openFrame: OpenFrame,clk_div=1, uart_pins={"tx": 6, "rx": 5}) -> None:
        super().__init__(openFrame.caravelEnv,uart_pins=uart_pins)
        self.openFrame = openFrame
        self.bit_time_ns = round(self.period *(2 + clk_div))  
        cocotb.log.info(f"[OpenFrameUART] configure UART bit_time_ns = {self.bit_time_ns}ns")
        self.uart_pins = uart_pins

    def change_clk_div(self, new_clk_div):
        self.bit_time_ns = round(self.period *(2 + new_clk_div))  
        cocotb.log.info(f"[OpenFrameUART] configure UART with new clk div {new_clk_div} bit_time_ns = {self.bit_time_ns}ns")

class OpenFrameSPI(SPI):
    def __init__(self, caravelEnv, clk_period=None, spi_pins={"CSB": 3, "SCK": 4, "SDO": 2, "SDI": 1}) -> None:
        super().__init__(caravelEnv, clk_period=clk_period,spi_pins=spi_pins)
        