from lora_e220 import LoRaE220, print_configuration, Configuration
from lora_e220_constants import OperatingFrequency, FixedTransmission, TransmissionPower, \
    AirDataRate, UARTParity, UARTBaudRate, RssiAmbientNoiseEnable, SubPacketSetting, WorPeriod, \
    LbtEnableByte, RssiEnableByte, TransmissionPower22
from lora_e220_operation_constant import ResponseStatusCode
import serial

from lora_e220_constants import FixedTransmission, RssiEnableByte

# Настройки UART для приемника
uart_port_receiver = '/dev/ttyS0'  # Замените на ваш порт UART для приемника
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
aux_pin_receiver = 121   # GPIO номер для AUX
m0_pin_receiver = 73   # GPIO номер для M0
m1_pin_receiver = 74   # GPIO номер для M1

# Создаем объект LoRaE220 для приемника
lora = LoRaE220('400T22D', uart_receiver, aux_pin=aux_pin_receiver, m0_pin=m0_pin_receiver, m1_pin=m1_pin_receiver)

# Initialize the LoRa module and print the initialization status code
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

##########################################################################################
# GET CONFIGURATION
##########################################################################################

# Retrieve the current configuration of the LoRa module and print it to the console
code, configuration = lora.get_configuration()
print("Retrieve configuration: {}", ResponseStatusCode.get_description(code))
print("------------- CONFIGURATION BEFORE CHANGE -------------")
print_configuration(configuration)

##########################################################################################
# SET CONFIGURATION
# To set the configuration, you must set the configuration with the new values
##########################################################################################

# Create a new Configuration object with the desired settings
configuration_to_set = Configuration('400T22D')
configuration_to_set.ADDL = 0x02
configuration_to_set.ADDH = 0x01
configuration_to_set.CHAN = 23

configuration_to_set.SPED.airDataRate = AirDataRate.AIR_DATA_RATE_100_96
configuration_to_set.SPED.uartParity = UARTParity.MODE_00_8N1
configuration_to_set.SPED.uartBaudRate = UARTBaudRate.BPS_9600

configuration_to_set.OPTION.transmissionPower = TransmissionPower('400T22D').\
                                                    get_transmission_power().POWER_10
# or
# configuration_to_set.OPTION.transmissionPower = TransmissionPower22.POWER_10

configuration_to_set.OPTION.RSSIAmbientNoise = RssiAmbientNoiseEnable.RSSI_AMBIENT_NOISE_ENABLED
configuration_to_set.OPTION.subPacketSetting = SubPacketSetting.SPS_064_10

configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
configuration_to_set.TRANSMISSION_MODE.WORPeriod = WorPeriod.WOR_1500_010
configuration_to_set.TRANSMISSION_MODE.enableLBT = LbtEnableByte.LBT_DISABLED
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED

configuration_to_set.CRYPT.CRYPT_H = 1
configuration_to_set.CRYPT.CRYPT_L = 1


# Set the new configuration on the LoRa module and print the updated configuration to the console
code, confSetted = lora.set_configuration(configuration_to_set)
print("------------- CONFIGURATION AFTER CHANGE -------------")
print(ResponseStatusCode.get_description(code))
print_configuration(confSetted)

##########################################################################################
# RESTORE DEFAULT CONFIGURATION
# To restore the default configuration, you must set the configuration with the default values
##########################################################################################

# Set the configuration to default values and print the updated configuration to the console
print("------------- RESTORE ALL DEFAULT -------------")
configuration_to_set = Configuration('400T22D')
code, confSetted = lora.set_configuration(configuration_to_set)
print(ResponseStatusCode.get_description(code))
print_configuration(confSetted)
