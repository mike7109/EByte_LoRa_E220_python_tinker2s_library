import serial
import time
from lora_e220 import LoRaE220, UARTParity, UARTBaudRate, ResponseStatusCode

# Настройки UART для отправителя
uart_port_sender = '/dev/ttyS0'  # Замените на ваш порт UART для отправителя
uart_baudrate = 9600

# Создаем объект UART для отправителя
uart_sender = serial.Serial(
    port=uart_port_sender,
    baudrate=uart_baudrate,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# GPIO номера для отправителя (замените на ваши номера пинов)
aux_pin_sender = 8   # GPIO номер для AUX
m0_pin_sender = 73   # GPIO номер для M0
m1_pin_sender = 74   # GPIO номер для M1

# Создаем объект LoRaE220 для отправителя
lora_sender = LoRaE220('400T22D', uart_sender, aux_pin=aux_pin_sender, m0_pin=m0_pin_sender, m1_pin=m1_pin_sender)

# Инициализируем модуль отправителя
code = lora_sender.begin()
if code != ResponseStatusCode.E220_SUCCESS:
    print(f'Ошибка инициализации отправителя: {code}')
else:
    print('Модуль отправителя успешно инициализирован')

# Отправляем тестовое сообщение
message = 'Привет от отправителя!'
code = lora_sender.send_transparent_message(message)
if code != ResponseStatusCode.E220_SUCCESS:
    print(f'Ошибка отправки сообщения: {code}')
else:
    print('Сообщение успешно отправлено')

# Завершаем работу с модулем отправителя
lora_sender.end()
