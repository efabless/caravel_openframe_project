import cocotb
from models.flash_spi_model.flash_spi_monitor import FlashSPI_Monitor
from cocotb.queue import Queue
from collections import namedtuple
import logging
from tabulate import tabulate


SPI_Operation = namedtuple("SPI_Operation", ["command", "address", "data_in", "data_out"])


class FlashSPI_Model():
    def __init__(self, dut_hdl) -> None:
        pass
        dbus_queue = Queue()
        FlashSPI_Monitor(dut_hdl, dbus_queue)
        FlashSPI_ModelP(dbus_queue)


class AbstractModelFlashSPI():
    def __init__(self, queue) -> None:
        self._thread = cocotb.scheduler.add(self._model(queue))

    async def _model(self, queue):
        pass

    async def _get_transactions(self, queue):
        transaction = await queue.get()
        cocotb.log.debug(f"[{__class__.__name__}][_get_transactions] getting transaction {transaction} from monitor")
        return transaction

    def configure_logger(self, logger_name="logger", logger_file="log.txt"):
        self.model_logger = logging.getLogger(logger_name)

        # Configure the logger
        self.model_logger.setLevel(logging.INFO)

        # Create a FileHandler to log to a file
        file_handler = logging.FileHandler(logger_file)
        file_handler.setLevel(logging.INFO)

        # # Create a StreamHandler to log to the console (optional)
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.DEBUG)

        # Add the handlers to the logger
        self.model_logger.addHandler(file_handler)
        # Create a NullHandler for the console to suppress output

        # self.model_logger.addHandler(console_handler)  # Optional: Log to console
        # Remove the console handler to avoid logging to console

        # log the header
        self.log_operation(None, header_logged=True)

    def log_operation(self, transaction, header_logged):
        pass


class FlashSPI_ModelP(AbstractModelFlashSPI):
    def __init__(self, queue) -> None:
        self.configure_logger(logger_name="Flash_SPI_LOG", logger_file="flash_spi.log")
        super().__init__(queue)

    async def _model(self, queue):
        bits_counter = -1
        command = address = data_write = data_read = ""
        data_in = []
        data_out = []
        spi_operation = SPI_Operation(command=0, address=0, data_in=0, data_out=0)
        while True:
            transaction = await self._get_transactions(queue)
            bits_counter += 1
            cocotb.log.debug(f"[{__class__.__name__}][_model] {transaction}")
            if transaction.cs == 1:
                bits_counter = -1
                command = address = data_write = data_read = ""
                data_in = []
                data_out = []
                continue
            elif bits_counter < 8:
                command += str(transaction.sdi)
            elif bits_counter < 32:
                address += str(transaction.sdi)
            else: 
                data_write += str(transaction.sdi)
                data_read += str(transaction.sdo)
                if (bits_counter - 15) % 8 == 0:  # if it's multiple of 8 bits
                    data_in.append(hex(int(data_write, 2)))
                    data_write = ""
                    data_out.append(hex(int(data_read, 2)))
                    data_read = ""
                    spi_operation = SPI_Operation(command="read" if command=="00000011" else command, address=hex(int(address,2)), data_in=data_in, data_out=data_out)
                    self.log_operation(spi_operation)

    def log_operation(self, transaction, header_logged=False):
        if header_logged:
            # Log the header
            header = tabulate([], headers=["Time", "Command", "Address",  "Data Out"], tablefmt="grid")
            self.model_logger.info(header)
            # Mark that the header has been logged
        else:
            table_data = [(
                f"{cocotb.utils.get_sim_time(units='ns')} ns",
                transaction.command,
                transaction.address,
                transaction.data_out
            )]
            table = tabulate(table_data, tablefmt="grid")
            self.model_logger.info(table)
