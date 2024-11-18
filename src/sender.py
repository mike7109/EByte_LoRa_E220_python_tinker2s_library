import serial

from lora_e220 import LoRaE220, Configuration
from lora_e220_constants import RssiAmbientNoiseEnable, RssiEnableByte
from lora_e220_operation_constant import ResponseStatusCode

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
aux_pin_sender = 121   # GPIO номер для AUX
m0_pin_sender = 73   # GPIO номер для M0
m1_pin_sender = 74   # GPIO номер для M1

# Создаем объект LoRaE220 для отправителя
lora = LoRaE220('400T22D', uart_sender, m0_pin=m0_pin_sender, m1_pin=m1_pin_sender)

code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('400T22D')
# To enable RSSI, you must also enable RSSI on receiver
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}", ResponseStatusCode.get_description(code))

# Send a string message (transparent)
message = 'Hello, world!'
code = lora.send_transparent_message(message)
print("Send message: {}", ResponseStatusCode.get_description(code))
