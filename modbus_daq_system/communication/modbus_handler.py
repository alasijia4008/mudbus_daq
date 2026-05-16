from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import logging
from typing import Callable, Optional, List
import threading
import struct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModbusHandler:
    def __init__(self):
        self.client: Optional[ModbusSerialClient] = None
        self.connected = False
        self._read_callback: Optional[Callable] = None
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    def set_read_callback(self, callback: Callable[[List[int], float], None]):
        self._read_callback = callback

    def connect(self, port: str, baudrate: int = 9600, parity: str = 'N',
                stopbits: int = 1, bytesize: int = 8, timeout: int = 1) -> bool:
        try:
            parity_map = {'N': 'N', 'E': 'E', 'O': 'O'}
            mapped_parity = parity_map.get(parity, 'N')

            self.client = ModbusSerialClient(
                port=port,
                baudrate=baudrate,
                parity=mapped_parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )

            result = self.client.connect()
            if result:
                self.connected = True
                logger.info(f"Connected to {port} at {baudrate} baud")
                return True
            else:
                logger.error(f"Failed to connect to {port}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        self.stop_polling()
        if self.client:
            self.client.close()
            self.client = None
        self.connected = False
        logger.info("Disconnected")

    def read_holding_registers(self, address: int, count: int, slave: int = 1) -> Optional[List[int]]:
        if not self.connected or not self.client:
            logger.warning("Not connected")
            return None

        try:
            result = self.client.read_holding_registers(
                address=address,
                count=count,
                device_id=slave
            )

            if result is None:
                logger.error("Modbus result is None")
                return None

            if result.isError():
                logger.error(f"Modbus error: {result}")
                return None

            registers = list(result.registers) if hasattr(result, 'registers') else None
            if registers is not None:
                logger.debug(f"Read {len(registers)} registers from address {address}: {registers}")
                return registers
            else:
                logger.error("No registers in result")
                return None
        except ModbusException as e:
            logger.error(f"Modbus exception: {e}")
            return None
        except Exception as e:
            logger.error(f"Read error: {type(e).__name__}: {e}")
            return None

    def write_single_register(self, address: int, value: int, slave: int = 1) -> bool:
        if not self.connected or not self.client:
            logger.warning("Not connected")
            return False

        try:
            result = self.client.write_register(
                address=address,
                value=value,
                device_id=slave
            )

            if result.isError():
                logger.error(f"Write error: {result}")
                return False

            logger.info(f"Write {value} to register {address}")
            return True
        except Exception as e:
            logger.error(f"Write exception: {e}")
            return False

    def write_multiple_registers(self, address: int, values: List[int], slave: int = 1) -> bool:
        if not self.connected or not self.client:
            logger.warning("Not connected")
            return False

        try:
            result = self.client.write_registers(
                address=address,
                values=values,
                device_id=slave
            )

            if result.isError():
                logger.error(f"Write multiple error: {result}")
                return False

            logger.info(f"Wrote {len(values)} registers starting at {address}")
            return True
        except Exception as e:
            logger.error(f"Write multiple exception: {e}")
            return False

    def start_polling(self, address: int, count: int, slave: int = 1, interval: int = 1000):
        self._stop_polling.clear()

        def poll_loop():
            import time
            while not self._stop_polling.is_set():
                try:
                    registers = self.read_holding_registers(address, count, slave)
                    if registers is not None and self._read_callback:
                        self._read_callback(registers, time.time())
                except Exception as e:
                    logger.error(f"Polling error: {e}")

                self._stop_polling.wait(interval / 1000.0)

        self._polling_thread = threading.Thread(target=poll_loop, daemon=True)
        self._polling_thread.start()
        logger.info(f"Started polling at {interval}ms interval")

    def stop_polling(self):
        self._stop_polling.set()
        if self._polling_thread and self._polling_thread.is_alive():
            self._polling_thread.join(timeout=2)
        logger.info("Stopped polling")

    @staticmethod
    def decode_float32(registers: List[int], byte_order: str = 'big') -> float:
        if len(registers) < 2:
            raise ValueError("Need at least 2 registers for float32")

        if byte_order == 'big':
            data = struct.pack('>HH', registers[0], registers[1])
            return struct.unpack('>f', data)[0]
        else:
            data = struct.pack('<HH', registers[0], registers[1])
            return struct.unpack('<f', data)[0]

    @staticmethod
    def decode_int32(registers: List[int], byte_order: str = 'big', signed: bool = True) -> int:
        if len(registers) < 2:
            raise ValueError("Need at least 2 registers for int32")

        if byte_order == 'big':
            data = struct.pack('>HH', registers[0], registers[1])
            return struct.unpack('>i' if signed else '>I', data)[0]
        else:
            data = struct.pack('<HH', registers[0], registers[1])
            return struct.unpack('<i' if signed else '<I', data)[0]

    @staticmethod
    def get_available_ports() -> List[str]:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
