import smbus
import time

bus = smbus.SMBus(1)

bus.write_byte_data(0x20, 0x00, 0x00)

time.sleep(0.5)

bus.write_byte_data(0x20, 0x06, 0x00)

time.sleep(0.5)

for x in range(0,10):
	bus.write_byte_data(0x20, 0x09, 0xFF)
	time.sleep(0.5)
	bus.write_byte_data(0x20, 0x09, 0x00)
	time.sleep(0.5)