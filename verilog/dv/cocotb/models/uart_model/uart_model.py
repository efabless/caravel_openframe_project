import cocotb
from cocotb.queue import Queue
from models.uart_model.uart_monitor import UART_Monitor
from models.uart_model.uart_coverage import UART_Coverage
import logging
from collections import namedtuple
from tabulate import tabulate


class UART_Model():
    def __init__(self, caravelEnv) -> None:
        self.caravelEnv = caravelEnv
        uart_queue = Queue()
        UART_Monitor(self.caravelEnv, uart_queue=uart_queue)
        UART_ModelP(uart_queue)


class AbstractModelUART():
    def __init__(self, queue) -> None:
        self._thread = cocotb.scheduler.add(self._model(queue))

    async def _model(self, queue):
        pass

    async def _get_transactions(self, queue):
        transaction = await queue.get()
        cocotb.log.debug(f"[{__class__.__name__}][_get_transactions] getting transaction {transaction} from monitor")
        return transaction

    def configure_logger(self, logger_name="logger", logger_file="log.txt"):
        self.spi_logger = logging.getLogger(logger_name)

        # Configure the logger
        self.spi_logger.setLevel(logging.INFO)

        # Create a FileHandler to log to a file
        file_handler = logging.FileHandler(logger_file)
        file_handler.setLevel(logging.INFO)

        # # Create a StreamHandler to log to the console (optional)
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.DEBUG)

        # Add the handlers to the logger
        self.spi_logger.addHandler(file_handler)
        # Create a NullHandler for the console to suppress output

        # self.spi_logger.addHandler(console_handler)  # Optional: Log to console
        # Remove the console handler to avoid logging to console

        # log the header
        self.log_operation(None, header_logged=True)

    def log_operation(self, transaction, header_logged):
        pass


class UART_ModelP(AbstractModelUART):
    def __init__(self, queue) -> None:
        self.configure_logger(logger_name="UART_LOG", logger_file="uart_log.log")
        super().__init__(queue)

    async def _model(self, queue):
        uart_cov = UART_Coverage()
        while True:
            transaction = await self._get_transactions(queue)
            self.log_operation(transaction)
            uart_cov.uart_cov(transaction)

    def log_operation(self, transaction, header_logged=False):
        if header_logged:
            # Log the header
            header = tabulate([], headers=["Time","Type", "character", "clock divider"], tablefmt="grid")
            self.spi_logger.info(header)
            # Mark that the header has been logged
        else:
            table_data = [(
                f"{cocotb.utils.get_sim_time(units='ns')} ns",
                transaction.type,
                transaction.char,
                transaction.clock_div
            )]
            table = tabulate(table_data, tablefmt="grid")
            self.spi_logger.info(table)

