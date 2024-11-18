import serial
import time
from lora_e220 import LoRaE220, Configuration
from lora_e220_operation_constant import ResponseStatusCode

from lora_e220_constants import FixedTransmission, RssiEnableByte

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
lora = LoRaE220('400T22D', uart_receiver, aux_pin=aux_pin_receiver, m0_pin=m0_pin_receiver, m1_pin=m1_pin_receiver)

# Инициализируем модуль приемника
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('400T22D')
configuration_to_set.ADDH = 0x00 # Address of this receive no sender
configuration_to_set.ADDL = 0x01 # Address of this receive no sender
configuration_to_set.CHAN = 23 # Address of this receive no sender
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
# To enable RSSI, you must also enable RSSI on sender
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED

code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}", ResponseStatusCode.get_description(code))

print("Waiting for messages...")
while True:
    if lora.available() > 0:
        # If the sender not set RSSI
        # code, value = lora.receive_message()
        # If the sender set RSSI
        code, value, rssi = lora.receive_message(rssi=True)
        print('RSSI: ', rssi)

        print(ResponseStatusCode.get_description(code))

        print(value)
        time.sleep(2)
