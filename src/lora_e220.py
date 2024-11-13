from lora_e220_constants import UARTParity, UARTBaudRate, TransmissionPower, FixedTransmission, AirDataRate, \
    OperatingFrequency, LbtEnableByte, WorPeriod, RssiEnableByte, RssiAmbientNoiseEnable, SubPacketSetting
from lora_e220_operation_constant import ResponseStatusCode, ModeType, ProgramCommand, SerialUARTBaudRate, \
    PacketLength, RegisterAddress

import re
import time
import json
from periphery import GPIO  # Импортируем GPIO из python-periphery
import serial

class Logger:
    def __init__(self, enable_debug):
        self.enable_debug = enable_debug
        self.name = ''

    def debug(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' DEBUG ', msg, *args)

    def info(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' INFO ', msg, *args)

    def error(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' ERROR ', msg, *args)

    def getLogger(self, name):
        self.name = name
        return Logger(self.enable_debug)


logging = Logger(False)

logger = logging.getLogger(__name__)

BROADCAST_ADDRESS = 0xFF

# (Остальные классы остаются без изменений)

# Обновляем класс LoRaE220 для использования periphery.GPIO

class LoRaE220:
    # Конструктор, принимающий объект UART напрямую
    def __init__(self, model, uart, aux_pin=None, m0_pin=None, m1_pin=None):
        self.uart = uart
        self.model = model

        pattern = '^(230|400|900)(T|R|MM|M)(22|30)[SD]$'

        model_regex = re.compile(pattern)
        if not model_regex.match(model):
            raise ValueError('Invalid model')

        self.aux_pin_num = aux_pin
        self.m0_pin_num = m0_pin
        self.m1_pin_num = m1_pin

        self.aux_pin = None
        self.m0_pin = None
        self.m1_pin = None

        self.uart_baudrate = uart.baudrate  # Должно быть 9600 для конфигурации
        self.uart_parity = uart.parity  # Должно соответствовать модулю
        self.uart_stop_bits = uart.stopbits  # Должно соответствовать модулю

        self.mode = None

    def begin(self, uart_parity=UARTParity.MODE_00_8N1):
        if not self.uart.is_open:
            self.uart.open()

        self.uart.reset_input_buffer()
        self.uart.reset_output_buffer()

        # Инициализируем GPIO
        if self.aux_pin_num is not None:
            self.aux_pin = GPIO(self.aux_pin_num, "in")

        if self.m0_pin_num is not None:
            self.m0_pin = GPIO(self.m0_pin_num, "out")
            self.m0_pin.write(False)  # Начальное состояние LOW

        if self.m1_pin_num is not None:
            self.m1_pin = GPIO(self.m1_pin_num, "out")
            self.m1_pin.write(False)  # Начальное состояние LOW

        code = self.set_mode(ModeType.MODE_0_NORMAL)
        if code != ResponseStatusCode.E220_SUCCESS:
            return code

        return code

    def set_mode(self, mode: ModeType) -> ResponseStatusCode:
        self.managed_delay(40)

        if self.m0_pin is None and self.m1_pin is None:
            logger.debug(
                "The M0 and M1 pins are not set, which means that you are connecting the pins directly as you need!")
        else:
            if mode == ModeType.MODE_0_NORMAL:
                # Mode 0 | normal operation
                self.m0_pin.write(False)
                self.m1_pin.write(False)
                logger.debug("MODE NORMAL!")
            elif mode == ModeType.MODE_1_WOR_TRANSMITTER:
                # Mode 1 | wake-up operation
                self.m0_pin.write(True)
                self.m1_pin.write(False)
                logger.debug("MODE WOR TRANSMITTER!")
            elif mode == ModeType.MODE_2_POWER_SAVING:
                # Mode 2 | power saving operation
                self.m0_pin.write(False)
                self.m1_pin.write(True)
                logger.debug("MODE WOR RECEIVER!")
            elif mode == ModeType.MODE_3_CONFIGURATION:
                # Mode 3 | Setting operation
                self.m0_pin.write(True)
                self.m1_pin.write(True)
                logger.debug("MODE PROGRAM!")
            else:
                return ResponseStatusCode.ERR_E220_INVALID_PARAM

        self.managed_delay(40)

        res = self.wait_complete_response(1000)
        if res == ResponseStatusCode.E220_SUCCESS:
            self.mode = mode

        return res

    @staticmethod
    def managed_delay(timeout):
        time.sleep(timeout / 1000.0)

    def wait_complete_response(self, timeout, wait_no_aux=100) -> ResponseStatusCode:
        result = ResponseStatusCode.E220_SUCCESS
        t_start = time.time()

        if self.aux_pin is not None:
            while not self.aux_pin.read():
                if (time.time() - t_start) * 1000 > timeout:
                    result = ResponseStatusCode.ERR_E220_TIMEOUT
                    logger.debug("Timeout error!")
                    return result

            logger.debug("AUX HIGH!")
        else:
            self.managed_delay(wait_no_aux)
            logger.debug("Wait no AUX pin!")

        self.managed_delay(20)
        logger.debug("Complete!")
        return result

    # (Остальные методы остаются без изменений)

    def end(self) -> ResponseStatusCode:
        try:
            if self.uart is not None:
                self.uart.close()
                del self.uart

            # Закрываем GPIO
            if self.aux_pin is not None:
                self.aux_pin.close()
                self.aux_pin = None
            if self.m0_pin is not None:
                self.m0_pin.close()
                self.m0_pin = None
            if self.m1_pin is not None:
                self.m1_pin.close()
                self.m1_pin = None

            return ResponseStatusCode.E220_SUCCESS

        except Exception as E:
            logger.error("Error: {}".format(E))
            return ResponseStatusCode.ERR_E220_DEINIT_UART_FAILED

# Основной скрипт
def main():
    # Настройки UART
    uart_port = '/dev/ttyS0'  # Замените на ваш порт UART
    uart_baudrate = 9600

    # Создаем объект UART
    uart = serial.Serial(
        port=uart_port,
        baudrate=uart_baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    # Пины GPIO (номера пинов соответствуют номерам линий в gpiochip0)
    aux_pin = 4  # Замените на ваш пин AUX
    m0_pin = 17  # Замените на ваш пин M0
    m1_pin = 27  # Замените на ваш пин M1

    # Создаем объект LoRaE220
    # lora = LoRaE220('400T22D', uart, aux_pin=aux_pin, m0_pin=m0_pin, m1_pin=m1_pin)
    lora = LoRaE220('400T22D', uart)

    # Инициализируем модуль
    code = lora.begin()
    if code != 0:
        print(f'Ошибка инициализации: {code}')
    else:
        print('Модуль успешно инициализирован')

    # Отправляем тестовое сообщение
    message = 'Привет, мир!'
    code = lora.send_transparent_message(message)
    if code != 0:
        print(f'Ошибка отправки сообщения: {code}')
    else:
        print('Сообщение успешно отправлено')

    # Завершаем работу с модулем
    lora.end()

if __name__ == "__main__":
    main()
