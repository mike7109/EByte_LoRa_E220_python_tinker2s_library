import serial
import time
from lora_e220 import LoRaE220, UARTParity, UARTBaudRate, ResponseStatusCode

# Настройки UART для приемника
uart_port_receiver = '/dev/ttyS4'  # Замените на ваш порт UART для приемника
uart_baudrate = 9600

# Создаем объект UART для приемника
uart_receiver = serial.Serial(
    port=uart_port_receiver,
    baudrate=uart_baudrate,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# GPIO номера для приемника (замените на ваши номера пинов)
aux_pin_receiver = 84   # GPIO номер для AUX
m0_pin_receiver = 149   # GPIO номер для M0
m1_pin_receiver = 85   # GPIO номер для M1

# Создаем объект LoRaE220 для приемника
lora_receiver = LoRaE220('400T22D', uart_receiver, aux_pin=aux_pin_receiver, m0_pin=m0_pin_receiver, m1_pin=m1_pin_receiver)

# Инициализируем модуль приемника
code = lora_receiver.begin()
if code != ResponseStatusCode.E220_SUCCESS:
    print(f'Ошибка инициализации приемника: {code}')
else:
    print('Модуль приемника успешно инициализирован')

# Ожидаем и принимаем сообщение
print('Ожидание сообщения...')
while True:
    if lora_receiver.available() > 0:
        code, value = lora_receiver.receive_message()
        print(ResponseStatusCode.get_description(code))

        print(value)
        time.sleep(2)

# Завершаем работу с модулем приемника
lora_receiver.end()
